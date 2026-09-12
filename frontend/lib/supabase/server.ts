import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { getSupabaseAuthConfig } from "@/lib/supabase/env";

export async function createClient() {
    const cookieStore = await cookies();
    const { url, anonKey } = getSupabaseAuthConfig();

    if (!url || !anonKey) {
        throw new Error(
            "Supabase no está configurado. Revisá SUPABASE_URL y SUPABASE_SECRET_KEY en el .env de la raíz.",
        );
    }

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
