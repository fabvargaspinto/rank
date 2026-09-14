"use server";

import { provisionSession, type FetchDataResponse } from "@/lib/fetch_data";
import { createClient } from "@/lib/supabase/server";
import { invalidFormResponse, loginSchema } from "@/lib/validation/auth";

export async function loginCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const parsed = loginSchema.safeParse({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
    });

    if (!parsed.success) {
        return invalidFormResponse(parsed.error);
    }

    const supabase = await createClient();
    const { data, error } = await supabase.auth.signInWithPassword({
        email: parsed.data.email,
        password: parsed.data.password,
    });

    if (error || !data.session) {
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

    return {
        ...backend,
        message: "Sesión iniciada.",
    };
}
