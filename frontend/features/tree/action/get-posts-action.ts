"use server";

import {
    fetchPostsByUsername,
    type PostListResponse,
    type FetchDataResponse,
} from "@/lib/fetch_data";
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
