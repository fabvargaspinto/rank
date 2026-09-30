import "server-only";

import { fetchData } from "@/lib/api/client";
import type {
    FetchDataResponse,
    FollowerHistoryResponse,
    InstagramConnectResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";

export async function startInstagramConnect(
    accessToken: string,
): Promise<FetchDataResponse<InstagramConnectResponse>> {
    return fetchData<InstagramConnectResponse>("/me/instagram/connect", {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchInstagramConnection(
    accessToken: string,
): Promise<FetchDataResponse<InstagramConnectionResponse>> {
    return fetchData<InstagramConnectionResponse>("/me/instagram", {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function fetchInstagramFollowers(
    accessToken: string,
): Promise<FetchDataResponse<FollowerHistoryResponse>> {
    return fetchData<FollowerHistoryResponse>("/me/instagram/followers", {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}

export async function disconnectInstagram(
    accessToken: string,
): Promise<FetchDataResponse<null>> {
    return fetchData<null>("/me/instagram", {
        method: "DELETE",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}
