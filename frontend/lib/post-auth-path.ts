import { fetchCurrentUser, getCurrentUser } from "@/lib/api/profile";
import type { UserResponse } from "@/lib/api/types";

export const LOGIN_PATH = "/login";
export const DASHBOARD_START_PATH = "/dashboard/start";
export const DASHBOARD_TREE_PATH = "/dashboard/tree";

export function postAuthPathForUser(user: UserResponse | null | undefined) {
    return user?.name?.trim() ? DASHBOARD_TREE_PATH : DASHBOARD_START_PATH;
}

export async function postAuthPathForToken(accessToken: string) {
    const result = await fetchCurrentUser(accessToken);
    return postAuthPathForUser(result.data);
}

export async function getPostAuthPath() {
    const result = await getCurrentUser();

    if (result.status === 401) {
        return LOGIN_PATH;
    }

    return postAuthPathForUser(result.data);
}
