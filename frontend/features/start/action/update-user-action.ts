"use server";

import {
    parseUpdateProfileInput,
    type UpdateProfileDraft,
} from "@/features/profile/model";
import { updateUser } from "@/lib/api/profile";
import type { FetchDataResponse, UserResponse } from "@/lib/api/types";
import { getAuthSession } from "@/lib/supabase/session";

export type UpdateUserLinkInput = {
    url: string;
};

export type UpdateUserInput = UpdateProfileDraft;

export async function updateUserAction(
    input: UpdateUserInput,
): Promise<FetchDataResponse<UserResponse>> {
    const session = await getAuthSession();

    if (!session) {
        return {
            data: null,
            isError: true,
            message: "Tenés que iniciar sesión",
            status: 401,
        };
    }

    const parsed = parseUpdateProfileInput(input);

    if (!parsed.ok) {
        return {
            data: null,
            isError: true,
            message: parsed.error.message,
            status: parsed.error.status,
            field: parsed.error.field,
        };
    }

    return updateUser(session.accessToken, parsed.body);
}
