"use server";

import { AuthProvider } from "@/lib/auth-provider";
import { fetchData } from "@/lib/fetch_data";

export async function registerGoogleAction(email: string, providerId: string) {
    return fetchData<{ ok: boolean }>("/auth/register/oauth", {
        method: "POST",
        body: JSON.stringify({
            email,
            provider: AuthProvider.GOOGLE,
            provider_id: providerId,
        }),
    });
}
