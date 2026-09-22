"use server";

import {
    createComment,
    type CommentResponse,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

const TEXT_MAX_LENGTH = 280;

export type CreateCommentInput = {
    text: string;
    link?: string | null;
};

function httpsLink(value: string | null | undefined) {
    const link = value?.trim() ?? "";
    return link.startsWith("https://") ? link : null;
}

export async function createCommentAction(
    input: CreateCommentInput,
): Promise<FetchDataResponse<CommentResponse>> {
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
            message: "El comentario es obligatorio",
            status: 400,
        };
    }

    if (text.length > TEXT_MAX_LENGTH) {
        return {
            data: null,
            isError: true,
            message: `El comentario debe tener entre 1 y ${TEXT_MAX_LENGTH} caracteres`,
            status: 400,
        };
    }

    return createComment(session.authId, session.accessToken, {
        text,
        link: httpsLink(input.link),
    });
}
