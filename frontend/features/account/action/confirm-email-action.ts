"use server";

import { redirect } from "next/navigation";
import { provisionSession } from "@/lib/api/session";
import type { FetchDataResponse } from "@/lib/api/types";
import { otpType } from "@/lib/auth/email-otp-type";
import { allowPasswordRecovery } from "@/lib/auth/password-recovery";
import { authErrorQuery } from "@/lib/auth/auth-error";
import { postAuthPathForToken } from "@/lib/post-auth-path";
import { createAuthClient } from "@/lib/supabase/auth-client";

const RESET_PATH = "/reset-password";
const EXPIRED_LINK = `/login?${authErrorQuery("link_expired")}`;

export async function confirmEmailAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const tokenHash = String(formData.get("token_hash") ?? "").trim();
    const type = otpType(String(formData.get("type") ?? "").trim() || null);
    const code = String(formData.get("code") ?? "").trim();
    const next =
        String(formData.get("next") ?? "").trim() === RESET_PATH
            ? RESET_PATH
            : null;

    const supabase = await createAuthClient();
    const verified =
        tokenHash && type
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
        const errorCode =
            provisioned.status === 403 ? "not_allowed" : "provision_failed";
        redirect(`/login?${authErrorQuery(errorCode)}`);
    }

    if (type === "recovery" || next === RESET_PATH) {
        await allowPasswordRecovery();
        redirect(RESET_PATH);
    }

    redirect(await postAuthPathForToken(session.access_token));
}
