import "server-only";

import { createServerClient } from "@supabase/ssr";
import type { CookieOptions } from "@supabase/ssr";
import { cookies, headers } from "next/headers";
import type { NextRequest } from "next/server";
import { getSupabaseAuthConfig } from "@/lib/supabase/env";

function requireSupabaseSecretKey(): string {
    const secretKey = process.env.SUPABASE_SECRET_KEY?.trim();

    if (!secretKey) {
        throw new Error("Falta SUPABASE_SECRET_KEY");
    }

    return secretKey;
}

export function clientIpFromForwardedFor(
    value: string | null | undefined,
): string | undefined {
    const ip = value?.split(",")[0]?.trim();
    return ip || undefined;
}

/** Cliente de Auth con secret key + IP real para rate limits de Supabase. */
export async function createAuthClient() {
    const secretKey = requireSupabaseSecretKey();
    const cookieStore = await cookies();
    const clientIp = clientIpFromForwardedFor(
        (await headers()).get("x-forwarded-for"),
    );
    const { url } = getSupabaseAuthConfig();

    return createServerClient(url, secretKey, {
        cookies: {
            getAll() {
                return cookieStore.getAll();
            },
            setAll(cookiesToSet, responseHeaders) {
                void responseHeaders;
                try {
                    cookiesToSet.forEach(({ name, value, options }) =>
                        cookieStore.set(name, value, options),
                    );
                } catch {
                    // Called from a Server Component that cannot set cookies.
                }
            },
        },
        global: {
            headers: clientIp ? { "sb-forwarded-for": clientIp } : {},
        },
    });
}

type AuthCookieToSet = {
    name: string;
    value: string;
    options: CookieOptions;
};

/** Variante para proxy.ts (cookies sobre NextRequest / NextResponse). */
export function createAuthProxyClient(
    request: NextRequest,
    onSetCookies: (
        cookiesToSet: AuthCookieToSet[],
        responseHeaders: Record<string, string>,
    ) => void,
) {
    const secretKey = requireSupabaseSecretKey();
    const clientIp = clientIpFromForwardedFor(
        request.headers.get("x-forwarded-for"),
    );
    const { url } = getSupabaseAuthConfig();

    return createServerClient(url, secretKey, {
        cookies: {
            getAll() {
                return request.cookies.getAll();
            },
            setAll(cookiesToSet, responseHeaders) {
                onSetCookies(cookiesToSet, responseHeaders);
            },
        },
        global: {
            headers: clientIp ? { "sb-forwarded-for": clientIp } : {},
        },
    });
}
