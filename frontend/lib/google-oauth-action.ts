"use server";

import { redirect } from "next/navigation";
import { authErrorQuery } from "@/lib/auth/auth-error";
import { requestOrigin } from "@/lib/request-origin";
import { createAuthClient } from "@/lib/supabase/auth-client";

function fromQuery(from: string) {
    return from === "/register" ? "register" : "login";
}

function fromPath(from: string) {
    return from === "/register" ? "/register" : "/login";
}

export async function startGoogleOAuthAction(from: string) {
    const origin = await requestOrigin();
    const path = fromPath(from);
    const supabase = await createAuthClient();

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
            redirectTo: `${origin}/auth/callback?from=${fromQuery(from)}`,
            skipBrowserRedirect: true,
        },
    });

    if (error || !data.url) {
        redirect(`${path}?${authErrorQuery("oauth_failed")}`);
    }

    redirect(data.url);
}
