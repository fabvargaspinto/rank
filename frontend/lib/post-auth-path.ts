import { fetchCurrentUser, getCurrentUser } from "@/lib/api/profile";
import type { FetchDataResponse, UserResponse } from "@/lib/api/types";

export const LOGIN_PATH = "/login";
export const DASHBOARD_START_PATH = "/dashboard/start";
export const DASHBOARD_TREE_PATH = "/dashboard/tree";
export const DASHBOARD_UNAVAILABLE_PATH = "/dashboard/unavailable";

export function postAuthPathForUser(user: UserResponse | null | undefined) {
    return user?.name?.trim() ? DASHBOARD_TREE_PATH : DASHBOARD_START_PATH;
}

function pathFromUserResult(result: FetchDataResponse<UserResponse>) {
    if (result.status === 401) {
        return LOGIN_PATH;
    }

    if (result.isError || result.status !== 200 || result.data === null) {
        return DASHBOARD_UNAVAILABLE_PATH;
    }

    return postAuthPathForUser(result.data);
}

export async function postAuthPathForToken(accessToken: string) {
    return pathFromUserResult(await fetchCurrentUser(accessToken));
}

export async function getPostAuthPath() {
    return pathFromUserResult(await getCurrentUser());
}
