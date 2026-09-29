"use server";

import {
    fetchPostsByUsername,
    type CommentListResponse,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { COMMENTS_PAGE_SIZE } from "../comment-constants";

export async function getCommentsAction(
    username: string,
    options: { limit?: number; cursor?: string | null } = {},
): Promise<FetchDataResponse<CommentListResponse>> {
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
        limit: options.limit ?? COMMENTS_PAGE_SIZE,
        cursor: options.cursor,
    });
}
