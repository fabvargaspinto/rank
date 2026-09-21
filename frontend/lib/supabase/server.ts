import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { getSupabaseAuthConfig } from "@/lib/supabase/env";

type PendingCookie = {
    name: string;
    value: string;
    options?: Parameters<NextResponse["cookies"]["set"]>[2];
};

export async function createClient() {
    const cookieStore = await cookies();
    const { url, anonKey } = getSupabaseAuthConfig();

    return createServerClient(url, anonKey, {
        cookies: {
            getAll() {
                return cookieStore.getAll();
            },
            setAll(cookiesToSet, _headers) {
                try {
                    cookiesToSet.forEach(({ name, value, options }) =>
                        cookieStore.set(name, value, options),
                    );
                } catch {
                    // Called from a Server Component that cannot set cookies.
                }
            },
        },
    });
}

export async function createCallbackClient() {
    const cookieStore = await cookies();
    const { url, anonKey } = getSupabaseAuthConfig();
    const pendingCookies: PendingCookie[] = [];

    const supabase = createServerClient(url, anonKey, {
        cookies: {
            getAll() {
                return cookieStore.getAll();
            },
            setAll(cookiesToSet, _headers) {
                cookiesToSet.forEach(({ name, value, options }) => {
                    pendingCookies.push({ name, value, options });
                    try {
                        cookieStore.set(name, value, options);
                    } catch {
                        // Route Handler will copy these onto NextResponse.
                    }
                });
            },
        },
    });

    function redirect(url: string) {
        const response = NextResponse.redirect(url);
        pendingCookies.forEach(({ name, value, options }) => {
            response.cookies.set(name, value, options);
        });
        return response;
    }

    return { supabase, redirect };
}
