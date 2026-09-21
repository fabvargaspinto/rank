import { createClient } from "@/lib/supabase/server";

export type AuthSession = {
    accessToken: string;
    authId: string;
};

export async function getAuthSession(): Promise<AuthSession | null> {
    const supabase = await createClient();
    const { data: userData } = await supabase.auth.getUser();
    const { data: sessionData } = await supabase.auth.getSession();
    const accessToken = sessionData.session?.access_token;
    const authId = userData.user?.id ?? sessionData.session?.user?.id;

    if (!authId || !accessToken) {
        return null;
    }

    return {
        accessToken,
        authId,
    };
}
