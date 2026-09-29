import "server-only";

import { fetchData } from "@/lib/api/client";
import type {
    CreatePostRequest,
    FetchDataResponse,
    PostListResponse,
    PostResponse,
} from "@/lib/api/types";

export async function fetchPostsByUsername(
    username: string,
    options: { limit?: number; cursor?: string | null } = {},
): Promise<FetchDataResponse<PostListResponse>> {
    const params = new URLSearchParams();
    if (options.limit !== undefined) {
        params.set("limit", String(options.limit));
    }
    if (options.cursor) {
        params.set("cursor", options.cursor);
    }
    const query = params.toString();

    return fetchData<PostListResponse>(
        `/profiles/${encodeURIComponent(username)}/posts${query ? `?${query}` : ""}`,
    );
}

export async function createPost(
    accessToken: string,
    post: CreatePostRequest,
): Promise<FetchDataResponse<PostResponse>> {
    return fetchData<PostResponse>("/me/posts", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(post),
    });
}

export async function deletePost(
    accessToken: string,
    postId: string,
): Promise<FetchDataResponse<null>> {
    return fetchData<null>(`/me/posts/${encodeURIComponent(postId)}`, {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}
