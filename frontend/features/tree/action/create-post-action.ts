"use server";

import { httpsUrlError, postTextError } from "@/lib/domain-limits";
import { createPost } from "@/lib/api/posts";
import type { FetchDataResponse, PostResponse } from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export type CreatePostInput = {
    text: string;
    link?: string | null;
};

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

    const textError = postTextError(input.text);

    if (textError) {
        return {
            data: null,
            isError: true,
            message: textError,
            status: 400,
        };
    }

    const link = input.link?.trim() ?? "";
    const linkError = httpsUrlError(link);

    if (linkError) {
        return {
            data: null,
            isError: true,
            message: linkError,
            status: 400,
        };
    }

    return createPost(session.accessToken, {
        text: input.text.trim(),
        link: link || null,
    });
}
