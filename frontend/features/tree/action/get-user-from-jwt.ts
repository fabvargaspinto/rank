import { fetchUserByAuthId, type FetchDataResponse, type UserResponse } from "@/lib/fetch_data";
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

    return fetchUserByAuthId(session.authId, session.accessToken);
}
