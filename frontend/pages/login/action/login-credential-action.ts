"use server";

import { fetchData, type FetchDataResponse } from "@/lib/fetch_data";
import { createClient } from "@/lib/supabase/server";

export async function loginCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");

    const backend = await fetchData("/auth/login/email", {
        method: "POST",
        body: JSON.stringify({
            email,
            password,
        }),
    });

    if (backend.isError) {
        return backend;
    }

    const supabase = await createClient();
    const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
    });

    if (error) {
        return {
            data: null,
            isError: true,
            message: "Email o contraseña incorrectos",
            status: 401,
        };
    }

    return {
        ...backend,
        message: "Sesión iniciada.",
    };
}
