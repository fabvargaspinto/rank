"use server";

import { provisionSession, type FetchDataResponse } from "@/lib/fetch_data";
import { createClient } from "@/lib/supabase/server";
import { invalidFormResponse, registerSchema } from "@/lib/validation/auth";

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

    const supabase = await createClient();
    const { data, error } = await supabase.auth.signUp({
        email: parsed.data.email,
        password: parsed.data.password,
    });

    if (error) {
        return {
            data: null,
            isError: true,
            message: error.message.trim() || "No se pudo crear la cuenta.",
            status: 400,
        };
    }

    if (!data.session) {
        return {
            data: null,
            isError: false,
            message: "Revisá tu email para confirmar la cuenta.",
            status: 200,
        };
    }

    const backend = await provisionSession(data.session.access_token);

    if (backend.isError) {
        return backend;
    }

    return {
        ...backend,
        message: "Cuenta creada.",
    };
}
