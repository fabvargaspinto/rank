"use server";

import { fetchData, type FetchDataResponse } from "@/lib/fetch_data";

export async function loginCredentialAction(
    _prev: FetchDataResponse,
    formData: FormData,
): Promise<FetchDataResponse> {
    const email = String(formData.get("email") ?? "");
    const password = String(formData.get("password") ?? "");

    return fetchData("/auth/login/email", {
        method: "POST",
        body: JSON.stringify({
            email,
            password,
        }),
    });
}
