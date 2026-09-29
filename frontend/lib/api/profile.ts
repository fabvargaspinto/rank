import "server-only";

import { cache } from "react";
import { fetchData } from "@/lib/api/client";
import type {
    AvatarUploadResponse,
    FetchDataResponse,
    PublicProfileResponse,
    UpdateProfileRequest,
    UserResponse,
} from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export const fetchCurrentUser = cache(
    async (accessToken: string): Promise<FetchDataResponse<UserResponse>> => {
        return fetchData<UserResponse>("/me", {
            headers: {
                Authorization: `Bearer ${accessToken}`,
            },
        });
    },
);

export const getCurrentUser = cache(
    async (): Promise<FetchDataResponse<UserResponse>> => {
        const session = await getAuthSession();

        if (!session) {
            return {
                data: null,
                isError: true,
                message: "Tenés que iniciar sesión",
                status: 401,
            };
        }

        return fetchCurrentUser(session.accessToken);
    },
);

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

export async function updateUser(
    accessToken: string,
    profile: UpdateProfileRequest,
): Promise<FetchDataResponse<UserResponse>> {
    return fetchData<UserResponse>("/me", {
        method: "PATCH",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(profile),
    });
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

export async function uploadAvatar(
    accessToken: string,
    file: File,
): Promise<FetchDataResponse<AvatarUploadResponse>> {
    const body = new FormData();
    body.append("file", file);

    return fetchData<AvatarUploadResponse>("/me/avatar", {
        method: "PUT",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
        body,
    });
}
