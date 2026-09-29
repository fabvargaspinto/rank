"use server";

import {
    parseCreatePostInput,
    type CreatePostDraft,
} from "@/features/post/model";
import { createPost } from "@/lib/api/posts";
import type { FetchDataResponse, PostResponse } from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export type CreatePostInput = CreatePostDraft;

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

    const parsed = parseCreatePostInput(input);

    if (!parsed.ok) {
        return {
            data: null,
            isError: true,
            message: parsed.message,
            status: 400,
        };
    }

    return createPost(session.accessToken, parsed.payload);
}
