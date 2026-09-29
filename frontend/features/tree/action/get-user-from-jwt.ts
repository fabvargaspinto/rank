import { fetchCurrentUser } from "@/lib/api/profile";
import type { FetchDataResponse, UserResponse } from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export default async function getUserFromJwt(): Promise<
    FetchDataResponse<UserResponse>
> {
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
}
