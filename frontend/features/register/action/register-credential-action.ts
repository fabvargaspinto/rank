"use server";

import { provisionSession, type FetchDataResponse } from "@/lib/fetch_data";

import { createClient } from "@/lib/supabase/server";

export async function registerCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("passwordConfirmation") ?? "");

    if (password !== confirmPassword) {
        return {
            data: null,
            isError: true,
            message: "Las contraseñas no coinciden",
            status: 400,
        };
    }

    const supabase = await createClient();
    const { data, error } = await supabase.auth.signUp({
        email,
        password,
    });

    if (error) {
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
