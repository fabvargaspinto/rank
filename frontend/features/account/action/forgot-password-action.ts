"use server";

import type { FetchDataResponse } from "@/lib/api/types";
import { requestOrigin } from "@/lib/request-origin";
import { createAuthClient } from "@/lib/supabase/auth-client";
import { emailSchema, invalidFormResponse } from "@/lib/validation/auth";

const SENT_MESSAGE =
    "Si el email está registrado, te enviamos un enlace para elegir una contraseña nueva.";

export async function forgotPasswordAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const parsed = emailSchema.safeParse(String(formData.get("email") ?? ""));

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const supabase = await createAuthClient();
    const origin = await requestOrigin();
    const { error } = await supabase.auth.resetPasswordForEmail(parsed.data, {
        redirectTo: `${origin}/auth/confirm?next=/reset-password`,
    });

    if (error) {
        return {
            data: null,
            isError: true,
            message: "No se pudo enviar el email. Probá de nuevo.",
            status: 400,
        };
    }

    return {
        data: null,
        isError: false,
        message: SENT_MESSAGE,
        status: 200,
    };
}
