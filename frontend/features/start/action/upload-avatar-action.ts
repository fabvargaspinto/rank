"use server";

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

    const result = await uploadAvatar(session.authId, session.accessToken, file);

    return {
        ...result,
        data: result.data?.url ?? null,
    };
}
