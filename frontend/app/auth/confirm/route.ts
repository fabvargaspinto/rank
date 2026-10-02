import { redirect } from "next/navigation";
import type { EmailOtpType } from "@supabase/supabase-js";
import { provisionSession } from "@/lib/api/session";
import { postAuthPathForToken } from "@/lib/post-auth-path";
import { createAuthClient } from "@/lib/supabase/auth-client";

const RESET_PATH = "/reset-password";
const EXPIRED_LINK =
    "/login?error=" + encodeURIComponent("El enlace venció o no es válido");

function otpType(value: string | null): EmailOtpType | null {
    if (
        value === "signup" ||
        value === "invite" ||
        value === "magiclink" ||
        value === "recovery" ||
        value === "email_change" ||
        value === "email"
    ) {
        return value;
    }

    return null;
}

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const tokenHash = searchParams.get("token_hash");
    const type = otpType(searchParams.get("type"));
    const code = searchParams.get("code");
    const next =
        searchParams.get("next") === RESET_PATH ? RESET_PATH : null;
    const supabase = await createAuthClient();
    const verified = tokenHash && type
        ? await supabase.auth.verifyOtp({
              type,
              token_hash: tokenHash,
          })
        : code
          ? await supabase.auth.exchangeCodeForSession(code)
          : null;

    if (!verified || verified.error || !verified.data.session) {
        redirect(EXPIRED_LINK);
    }

    const session = verified.data.session;

    const provisioned = await provisionSession(session.access_token);

    if (provisioned.isError) {
        await supabase.auth.signOut();
        redirect(
            `/login?error=${encodeURIComponent(provisioned.message)}`,
        );
    }

    if (type === "recovery" || next === RESET_PATH) {
        redirect(RESET_PATH);
    }

    redirect(
        await postAuthPathForToken(session.access_token),
    );
}
