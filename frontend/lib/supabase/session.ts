import { createClient } from "@/lib/supabase/server";

export type AuthSession = {
    accessToken: string;
    authId: string;
};

export async function getAuthSession(): Promise<AuthSession | null> {
    const supabase = await createClient();
    const { data: userData, error: userError } = await supabase.auth.getUser();
    const user = userData.user;

    if (userError || !user?.id) {
        return null;
    }

    const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
    const accessToken = sessionData.session?.access_token;

    if (sessionError || !accessToken) {
        return null;
    }

    return {
        accessToken,
        authId: user.id,
    };
}
