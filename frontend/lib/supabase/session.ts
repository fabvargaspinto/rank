import { createClient } from "@/lib/supabase/server";

export type AuthSession = {
    accessToken: string;
    authId: string;
};

export async function getAuthSession(): Promise<AuthSession | null> {
    const supabase = await createClient();
    const { data, error } = await supabase.auth.getSession();
    const session = data.session;

    if (error || !session?.access_token || !session.user?.id) {
        return null;
    }

    return {
        accessToken: session.access_token,
        authId: session.user.id,
    };
}
