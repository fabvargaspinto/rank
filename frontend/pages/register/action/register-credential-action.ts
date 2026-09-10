"use server";

import { fetchData, type FetchDataResponse } from "@/lib/fetch_data";

export async function registerCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("passwordConfirmation") ?? "");

    return fetchData("/auth/register/email", {
        method: "POST",
        body: JSON.stringify({
            email,
            password,
            confirm_password: confirmPassword,
        }),
    });
}
