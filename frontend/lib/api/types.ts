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

export type UpdateProfileRequest = {
    name: string;
    display_name?: string | null;
    avatar?: string | null;
    description?: string | null;
    links?: { url: string }[] | null;
};

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

export type CreatePostRequest = {
    text: string;
    link?: string | null;
};

export type InstagramConnectResponse = {
    authorization_url: string;
};

export type InstagramConnectionResponse = {
    connected: boolean;
    username: string | null;
    instagram_account_id: string | null;
    followers_count: number | null;
    followers_delta: number | null;
};

export type FollowerHistoryItemResponse = {
    week_start: string;
    followers_count: number;
    captured_at: string;
    delta: number | null;
};

export type FollowerHistoryResponse = {
    items: FollowerHistoryItemResponse[];
};
