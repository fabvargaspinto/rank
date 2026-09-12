"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

async function originFromHeaders() {
    const headerStore = await headers();
    const origin = headerStore.get("origin");
    if (origin) {
        return origin;
    }

    const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
    const proto = headerStore.get("x-forwarded-proto") ?? "http";
    if (host) {
        return `${proto}://${host}`;
    }

    return "http://localhost:3000";
}

function fromQuery(from: string) {
    return from === "/register" ? "register" : "login";
}

function fromPath(from: string) {
    return from === "/register" ? "/register" : "/";
}

export async function startGoogleOAuthAction(from: string) {
    const origin = await originFromHeaders();
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
