"use server";

import {
    AVATAR_TOO_LARGE_MESSAGE,
    AVATAR_TYPE_MESSAGE,
    isAvatarMimeType,
    MAX_AVATAR_BYTES,
} from "@/lib/domain-limits";
import {
    uploadAvatar,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

export async function uploadAvatarAction(
    file: File,
): Promise<FetchDataResponse<string>> {
    const session = await getAuthSession();

    if (!session) {
        return {
            data: null,
            isError: true,
            message: "Tenés que iniciar sesión",
            status: 401,
        };
    }

    if (!isAvatarMimeType(file.type)) {
        return {
            data: null,
            isError: true,
            message: AVATAR_TYPE_MESSAGE,
            status: 400,
        };
    }

    if (file.size > MAX_AVATAR_BYTES) {
        return {
            data: null,
            isError: true,
            message: AVATAR_TOO_LARGE_MESSAGE,
            status: 400,
        };
    }

    const result = await uploadAvatar(session.accessToken, file);

    return {
        ...result,
        data: result.data?.url ?? null,
    };
}
