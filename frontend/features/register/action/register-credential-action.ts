"use server";

import { redirect } from "next/navigation";
import { provisionSession } from "@/lib/api/session";
import type { FetchDataResponse } from "@/lib/api/types";
import { postAuthPathForToken } from "@/lib/post-auth-path";
import { requestOrigin } from "@/lib/request-origin";
import { createAuthClient } from "@/lib/supabase/auth-client";
import { emailRateLimitResponse } from "@/lib/supabase/auth-email";
import { resolveCaptchaToken } from "@/lib/hcaptcha";
import { invalidFormResponse, registerSchema } from "@/lib/validation/auth";

const CHECK_EMAIL_MESSAGE = "Revisá tu email para confirmar la cuenta.";

export async function registerCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const parsed = registerSchema.safeParse({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
        passwordConfirmation: String(
            formData.get("passwordConfirmation") ?? "",
        ),
    });

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const captcha = await resolveCaptchaToken(formData);
    if (!captcha.ok) {
        return captcha.response;
    }

    const supabase = await createAuthClient();
    const origin = await requestOrigin();
    const { data, error } = await supabase.auth.signUp({
        email: parsed.data.email,
        password: parsed.data.password,
        options: {
            emailRedirectTo: `${origin}/auth/confirm`,
            ...(captcha.token ? { captchaToken: captcha.token } : {}),
        },
    });

    if (error) {
        if (
            error.code === "user_already_exists" ||
            error.code === "email_exists"
        ) {
            return {
                data: null,
                isError: false,
                message: CHECK_EMAIL_MESSAGE,
                status: 200,
            };
        }

        const rateLimited = emailRateLimitResponse(error);
        if (rateLimited) {
            return rateLimited;
        }

        return {
            data: null,
            isError: true,
            message: "No se pudo crear la cuenta.",
            status: 400,
        };
    }

    if (!data.session) {
        return {
            data: null,
            isError: false,
            message: CHECK_EMAIL_MESSAGE,
            status: 200,
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
