import { fetchUserByAuthId, type UserResponse } from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

export const LOGIN_PATH = "/login";
export const DASHBOARD_START_PATH = "/dashboard/start";
export const DASHBOARD_TREE_PATH = "/dashboard/tree";

export function postAuthPathForUser(user: UserResponse | null | undefined) {
    return user?.name?.trim() ? DASHBOARD_TREE_PATH : DASHBOARD_START_PATH;
}

export async function postAuthPathForToken(authId: string, accessToken: string) {
    const result = await fetchUserByAuthId(authId, accessToken);
    return postAuthPathForUser(result.data);
}

export async function getPostAuthPath() {
    const session = await getAuthSession();

    if (!session) {
        return LOGIN_PATH;
    }

    return postAuthPathForToken(session.authId, session.accessToken);
}
