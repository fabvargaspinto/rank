"use server";

import { redirect } from "next/navigation";
import {
    disconnectInstagram,
    fetchInstagramConnection,
    fetchInstagramFollowers,
    startInstagramConnect,
} from "@/lib/api/instagram";
import type {
    FetchDataResponse,
    FollowerHistoryResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

function unauthenticated<T>(): FetchDataResponse<T> {
    return {
        data: null,
        isError: true,
        message: "Tenés que iniciar sesión",
        status: 401,
    };
}

export async function connectInstagramAction(): Promise<
    FetchDataResponse<{ authorization_url: string }>
> {
    const session = await getAuthSession();

    if (!session) {
        return unauthenticated();
    }

    const result = await startInstagramConnect(session.accessToken);

    if (result.isError || !result.data?.authorization_url) {
        return result;
    }

    redirect(result.data.authorization_url);
}

export async function getInstagramConnectionAction(): Promise<
    FetchDataResponse<InstagramConnectionResponse>
> {
    const session = await getAuthSession();

    if (!session) {
        return unauthenticated();
    }

    return fetchInstagramConnection(session.accessToken);
}

export async function getInstagramFollowersAction(): Promise<
    FetchDataResponse<FollowerHistoryResponse>
> {
    const session = await getAuthSession();

    if (!session) {
        return unauthenticated();
    }

    return fetchInstagramFollowers(session.accessToken);
}

export async function disconnectInstagramAction(): Promise<
    FetchDataResponse<null>
> {
    const session = await getAuthSession();

    if (!session) {
        return unauthenticated();
    }

    return disconnectInstagram(session.accessToken);
}
