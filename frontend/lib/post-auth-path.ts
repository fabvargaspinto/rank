import { fetchCurrentUser, type UserResponse } from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

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
    const session = await getAuthSession();

    if (!session) {
        return LOGIN_PATH;
    }

    return postAuthPathForToken(session.accessToken);
}
