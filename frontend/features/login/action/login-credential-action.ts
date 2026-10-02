"use server";

import { redirect } from "next/navigation";
import { provisionSession } from "@/lib/api/session";
import type { FetchDataResponse } from "@/lib/api/types";
import { postAuthPathForToken } from "@/lib/post-auth-path";
import { requestOrigin } from "@/lib/request-origin";
import { createAuthClient } from "@/lib/supabase/auth-client";
import {
    emailRateLimitResponse,
    loginAuthErrorResponse,
} from "@/lib/supabase/auth-email";
import {
    emailSchema,
    invalidFormResponse,
    loginSchema,
} from "@/lib/validation/auth";

const RESENT_MESSAGE = "Te enviamos de nuevo el email de confirmación.";

async function resendConfirmation(
    formData: FormData,
): Promise<FetchDataResponse> {
    const parsed = emailSchema.safeParse(String(formData.get("email") ?? ""));

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const supabase = await createAuthClient();
    const origin = await requestOrigin();
    const { error } = await supabase.auth.resend({
        type: "signup",
        email: parsed.data,
        options: {
            emailRedirectTo: `${origin}/auth/confirm`,
        },
    });

    if (error) {
        const rateLimited = emailRateLimitResponse(error);
        if (rateLimited) {
            return rateLimited;
        }

        return {
            data: null,
            isError: true,
            message: "No se pudo reenviar el email. Probá de nuevo.",
            status: 400,
            code: "email_not_confirmed",
        };
    }

    return {
        data: null,
        isError: false,
        message: RESENT_MESSAGE,
        status: 200,
        code: "email_not_confirmed",
    };
}

export async function loginCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    if (String(formData.get("intent") ?? "") === "resend") {
        return resendConfirmation(formData);
    }

    const parsed = loginSchema.safeParse({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
    });

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const supabase = await createAuthClient();
    const { data, error } = await supabase.auth.signInWithPassword({
        email: parsed.data.email,
        password: parsed.data.password,
    });

    if (error || !data.session) {
        if (error) {
            return loginAuthErrorResponse(error);
        }
        return {
            data: null,
            isError: true,
            message: "Email o contraseña incorrectos",
            status: 401,
        };
    }

    const backend = await provisionSession(data.session.access_token);

    if (backend.isError) {
        return backend;
    }

    redirect(
        await postAuthPathForToken(data.session.access_token),
    );
}
