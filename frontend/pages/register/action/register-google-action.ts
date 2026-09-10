"use server";

import { AuthOauthProvider } from "@/lib/auth-oauth-provider";
import { fetchData } from "@/lib/fetch_data";

export async function registerGoogleAction(email: string, oauthProviderId: string) {
    return fetchData<{ ok: boolean }>("/auth/register/oauth", {
        method: "POST",
        body: JSON.stringify({
            email,
            oauth_provider: AuthOauthProvider.GOOGLE,
            oauth_provider_id: oauthProviderId,
        }),
    });
}
