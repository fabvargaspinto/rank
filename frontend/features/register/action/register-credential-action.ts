"use server";

import { redirect } from "next/navigation";
import { provisionSession } from "@/lib/api/session";
import type { FetchDataResponse } from "@/lib/api/types";
import { postAuthPathForToken } from "@/lib/post-auth-path";
import { requestOrigin } from "@/lib/request-origin";
import { createAuthClient } from "@/lib/supabase/auth-client";
import {
    TRIAL_REGISTRATION_DENIED,
    isTrialTester,
} from "@/lib/trial-testers";
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

    // trial testers
    if (!isTrialTester(parsed.data.email)) {
        return {
            data: null,
            isError: true,
            message: TRIAL_REGISTRATION_DENIED,
            status: 403,
        };
    }

    const supabase = await createAuthClient();
    const origin = await requestOrigin();
    const { data, error } = await supabase.auth.signUp({
        email: parsed.data.email,
        password: parsed.data.password,
        options: {
            emailRedirectTo: `${origin}/auth/confirm`,
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
