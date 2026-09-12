"use server";

import { startGoogleOAuthAction } from "@/lib/google-oauth-action";

export async function loginGoogleAction(_formData?: FormData) {
    await startGoogleOAuthAction("/");
}
