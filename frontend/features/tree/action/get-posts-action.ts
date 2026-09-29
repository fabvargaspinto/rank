"use server";

import { fetchPostsByUsername } from "@/lib/api/posts";
import type { FetchDataResponse, PostListResponse } from "@/lib/api/types";
import { POSTS_PAGE_SIZE } from "../post-constants";

export async function getPostsAction(
    username: string,
    options: { limit?: number; cursor?: string | null } = {},
): Promise<FetchDataResponse<PostListResponse>> {
    const name = username.trim();

    if (!name) {
        return {
            data: null,
            isError: true,
            message: "El usuario no existe",
            status: 404,
        };
    }

    return fetchPostsByUsername(name, {
        limit: options.limit ?? POSTS_PAGE_SIZE,
        cursor: options.cursor,
    });
}
