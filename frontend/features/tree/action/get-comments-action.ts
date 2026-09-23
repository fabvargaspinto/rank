"use server";

import {
    fetchCommentsByUserId,
    type CommentListResponse,
    type FetchDataResponse,
} from "@/lib/fetch_data";
import { COMMENTS_PAGE_SIZE } from "../comment-constants";

export async function getCommentsAction(
    userId: string,
    options: { limit?: number; offset?: number } = {},
): Promise<FetchDataResponse<CommentListResponse>> {
    const id = userId.trim();

    if (!id) {
        return {
            data: null,
            isError: true,
            message: "El usuario no existe",
            status: 404,
        };
    }

    return fetchCommentsByUserId(id, {
        limit: options.limit ?? COMMENTS_PAGE_SIZE,
        offset: options.offset ?? 0,
    });
}
