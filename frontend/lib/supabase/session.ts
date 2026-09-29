import { cache } from "react";
import { createClient } from "@/lib/supabase/server";

export type AuthSession = {
    accessToken: string;
    authId: string;
};

export const getAuthSession = cache(async (): Promise<AuthSession | null> => {
    const supabase = await createClient();
    const { data, error } = await supabase.auth.getClaims();
    const authId = data?.claims?.sub;

    if (error || typeof authId !== "string" || !authId) {
        return null;
    }

    // getClaims verifies the JWT. The API still needs the raw bearer token.
    const { data: sessionData } = await supabase.auth.getSession();
    const accessToken = sessionData.session?.access_token;

    if (!accessToken) {
        return null;
    }

    return {
        accessToken,
        authId,
    };
});
