import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { getSupabaseAuthConfig } from "@/lib/supabase/env";

export async function proxy(request: NextRequest) {
    let supabaseResponse = NextResponse.next({
        request,
    });

    const { url, anonKey } = getSupabaseAuthConfig();

    const supabase = createServerClient(url, anonKey, {
        cookies: {
            getAll() {
                return request.cookies.getAll();
            },
            setAll(cookiesToSet, headers) {
                cookiesToSet.forEach(({ name, value }) =>
                    request.cookies.set(name, value),
                );
                supabaseResponse = NextResponse.next({
                    request,
                });
                cookiesToSet.forEach(({ name, value, options }) =>
                    supabaseResponse.cookies.set(name, value, options),
                );
                if (headers) {
                    Object.entries(headers).forEach(([key, value]) => {
                        if (value) {
                            supabaseResponse.headers.set(key, value);
                        }
                    });
                }
            },
        },
    });

    const { data } = await supabase.auth.getClaims();
    const { pathname } = request.nextUrl;

    if (
        data?.claims &&
        (pathname === "/login" || pathname === "/register")
    ) {
        const redirectUrl = request.nextUrl.clone();
        redirectUrl.pathname = "/";
        redirectUrl.search = "";
        const redirectResponse = NextResponse.redirect(redirectUrl);
        supabaseResponse.cookies.getAll().forEach((cookie) => {
            redirectResponse.cookies.set(cookie);
        });
        return redirectResponse;
    }

    return supabaseResponse;
}

export const config = {
    matcher: [
        "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
    ],
};
