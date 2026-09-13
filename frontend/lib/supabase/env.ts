export function getSupabaseAuthConfig() {
    const url = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").trim();
    const anonKey = (process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "").trim();

    if (!url || !anonKey) {
        throw new Error(
            "Supabase no está configurado. Definí NEXT_PUBLIC_SUPABASE_URL y NEXT_PUBLIC_SUPABASE_ANON_KEY.",
        );
    }

    return {
        url,
        anonKey,
    };
}
