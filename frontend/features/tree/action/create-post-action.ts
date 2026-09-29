"use server";

import {
    createPost,
    type PostResponse,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

const TEXT_MAX_LENGTH = 280;

export type CreatePostInput = {
    text: string;
    link?: string | null;
};

function httpsLink(value: string | null | undefined) {
    const link = value?.trim() ?? "";
    return link.startsWith("https://") ? link : null;
}

export async function createPostAction(
    input: CreatePostInput,
): Promise<FetchDataResponse<PostResponse>> {
    const session = await getAuthSession();

    if (!session) {
        return {
            data: null,
            isError: true,
            message: "Tenés que iniciar sesión",
            status: 401,
        };
    }

    const text = input.text.trim();

    if (!text) {
        return {
            data: null,
            isError: true,
            message: "La publicación es obligatoria",
            status: 400,
        };
    }

    if (text.length > TEXT_MAX_LENGTH) {
        return {
            data: null,
            isError: true,
            message: `La publicación debe tener entre 1 y ${TEXT_MAX_LENGTH} caracteres`,
            status: 400,
        };
    }

    return createPost(session.accessToken, {
        text,
        link: httpsLink(input.link),
    });
}
