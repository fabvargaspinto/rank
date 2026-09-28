"use server";

import { redirect } from "next/navigation";
import { requestOrigin } from "@/lib/request-origin";
import { createClient } from "@/lib/supabase/server";

function fromQuery(from: string) {
    return from === "/register" ? "register" : "login";
}

function fromPath(from: string) {
    return from === "/register" ? "/register" : "/login";
}

export async function startGoogleOAuthAction(from: string) {
    const origin = await requestOrigin();
    const path = fromPath(from);
    const supabase = await createClient();

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
            redirectTo: `${origin}/auth/callback?from=${fromQuery(from)}`,
            skipBrowserRedirect: true,
        },
    });

    if (error || !data.url) {
        redirect(`${path}?error=${encodeURIComponent("No se pudo iniciar Google")}`);
    }

    redirect(data.url);
}
