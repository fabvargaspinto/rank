import "server-only";

import { fetchData } from "@/lib/api/client";
import type { FetchDataResponse, SessionResponse } from "@/lib/api/types";

export async function provisionSession(
    accessToken: string,
): Promise<FetchDataResponse<SessionResponse>> {
    return fetchData<SessionResponse>("/auth/session", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
}
