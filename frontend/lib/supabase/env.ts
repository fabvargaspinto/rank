export function getSupabaseAuthConfig() {
    const url = (
        process.env.NEXT_PUBLIC_SUPABASE_URL ||
        process.env.SUPABASE_URL ||
        ""
    ).trim();

    const anonKey = (
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
        process.env.SUPABASE_ANON_KEY ||
        process.env.SUPABASE_PUBLISHABLE_KEY ||
        ""
    ).trim();

    const key = anonKey || (process.env.SUPABASE_SECRET_KEY || "").trim();

    return {
        url,
        anonKey: key,
    };
}
