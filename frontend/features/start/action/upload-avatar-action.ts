"use server";

import {
    uploadAvatar,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

const MAX_AVATAR_BYTES = 2 * 1024 * 1024;
const AVATAR_MIME_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

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

    if (!AVATAR_MIME_TYPES.has(file.type)) {
        return {
            data: null,
            isError: true,
            message: "La imagen debe ser JPEG, PNG o WebP",
            status: 400,
        };
    }

    if (file.size > MAX_AVATAR_BYTES) {
        return {
            data: null,
            isError: true,
            message: "La imagen no puede superar 2 MB",
            status: 400,
        };
    }

    const result = await uploadAvatar(session.authId, session.accessToken, file);

    return {
        ...result,
        data: result.data?.url ?? null,
    };
}
