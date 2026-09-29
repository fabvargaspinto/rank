const API_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

export type FetchDataResponse<T = unknown> = {
    data: T | null;
    isError: boolean;
    message: string;
    status: number;
    code?: string;
    field?: string;
    requestId?: string;
};

const USERNAME_FIELD_CODES = new Set(["INVALID_USERNAME", "USERNAME_TAKEN"]);

export function isUsernameFieldError(error: {
    code?: string;
    field?: string;
}): boolean {
    return (
        error.field === "name" ||
        (error.code !== undefined && USERNAME_FIELD_CODES.has(error.code))
    );
}

export const emptyFetchResponse: FetchDataResponse = {
    data: null,
    isError: false,
    message: "",
    status: 0,
};

function messageFromBackend(data: unknown): string {
    if (!data || typeof data !== "object" || !("detail" in data)) {
        return "Request failed";
    }

    const { detail } = data;

    if (typeof detail === "string") {
        return detail;
    }

    if (Array.isArray(detail)) {
        return detail
            .map((item) =>
                item && typeof item === "object" && "msg" in item
                    ? String(item.msg)
                    : JSON.stringify(item),
            )
            .join(", ");
    }

    return "Request failed";
}

function errorMeta(data: unknown): { code?: string; field?: string } {
    if (!data || typeof data !== "object") {
        return {};
    }

    const record = data as { code?: unknown; field?: unknown };

    return {
        ...(typeof record.code === "string" ? { code: record.code } : {}),
        ...(typeof record.field === "string" ? { field: record.field } : {}),
    };
}

export type SessionResponse = {
    provisioned: boolean;
};

export type UserLinkResponse = {
    id: string;
    type: string;
    url: string;
    sort_index: number;
};

export type UserResponse = {
    id: string;
    name: string | null;
    display_name: string | null;
    avatar: string | null;
    description: string | null;
    links: UserLinkResponse[];
};

export async function provisionSession(
    accessToken: string,
): Promise<FetchDataResponse<SessionResponse>> {
    return fetchData<SessionResponse>("/auth/session", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchCurrentUser(
    accessToken: string,
): Promise<FetchDataResponse<UserResponse>> {
    return fetchData<UserResponse>("/me", {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchUserByName(
    name: string,
    options: { limit?: number } = {},
): Promise<FetchDataResponse<PublicProfileResponse>> {
    const params = new URLSearchParams();
    if (options.limit !== undefined) {
        params.set("limit", String(options.limit));
    }
    const query = params.toString();

    return fetchData<PublicProfileResponse>(
        `/profiles/${encodeURIComponent(name)}${query ? `?${query}` : ""}`,
    );
}

export async function deleteAccount(
    accessToken: string,
): Promise<FetchDataResponse<null>> {
    return fetchData<null>("/me", {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function updateUser(
    accessToken: string,
    profile: {
        name: string;
        display_name?: string | null;
        avatar?: string | null;
        description?: string | null;
        links?: { url: string }[] | null;
    },
): Promise<FetchDataResponse<UserResponse>> {
    return fetchData<UserResponse>("/me", {
        method: "PATCH",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(profile),
    });
}

export type AvatarUploadResponse = {
    url: string;
};

export type PostResponse = {
    id: string;
    user_id: string;
    text: string;
    link: string | null;
    created_at: string;
};

export type PostListResponse = {
    items: PostResponse[];
    next_cursor: string | null;
};

export type PublicProfileResponse = UserResponse & {
    posts: PostResponse[];
    next_cursor: string | null;
};

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
    post: {
        text: string;
        link?: string | null;
    },
): Promise<FetchDataResponse<PostResponse>> {
    return fetchData<PostResponse>(
        "/me/posts",
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify(post),
        },
    );
}

export async function deletePost(
    accessToken: string,
    postId: string,
): Promise<FetchDataResponse<null>> {
    return fetchData<null>(
        `/me/posts/${encodeURIComponent(postId)}`,
        {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        },
    );
}

export async function uploadAvatar(
    accessToken: string,
    file: File,
): Promise<FetchDataResponse<AvatarUploadResponse>> {
    const body = new FormData();
    body.append("file", file);

    return fetchData<AvatarUploadResponse>(
        "/me/avatar",
        {
            method: "PUT",
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
            body,
        },
    );
}

export async function fetchData<T = unknown>(
    path: string,
    options: RequestInit = {},
): Promise<FetchDataResponse<T>> {
    const url = path.startsWith("http") ? path : `${API_URL}${path}`;

    const requestId = crypto.randomUUID();

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...(options.body instanceof FormData
                    ? {}
                    : { "Content-Type": "application/json" }),
                "X-Request-ID": requestId,
                ...options.headers,
            },
        });

        const data = await response.json().catch(() => null);
        const echoedId =
            response.headers.get("X-Request-ID")?.trim() || requestId;

        if (!response.ok) {
            return {
                data: null,
                isError: true,
                message: messageFromBackend(data),
                status: response.status,
                requestId: echoedId,
                ...errorMeta(data),
            };
        }

        return {
            data: data as T,
            isError: false,
            message: "",
            status: response.status,
            requestId: echoedId,
        };
    } catch (error) {
        return {
            data: null,
            isError: true,
            message: error instanceof Error ? error.message : "Request failed",
            status: 0,
            requestId,
        };
    }
}
