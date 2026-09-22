"use server";

import {
    updateUser,
    type FetchDataResponse,
    type UserResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

const MAX_LINKS = 6;

export type UpdateUserLinkInput = {
    url: string;
};

export type UpdateUserInput = {
    name: string;
    avatar?: string | null;
    description?: string | null;
    links?: UpdateUserLinkInput[];
};

function httpsAvatar(value: string | null | undefined) {
    const avatar = value?.trim() ?? "";
    return avatar.startsWith("https://") ? avatar : null;
}

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

    const name = input.name.trim();

    if (!name) {
        return {
            data: null,
            isError: true,
            message: "El nombre es obligatorio",
            status: 400,
        };
    }

    const links = (input.links ?? [])
        .map((link) => ({ url: link.url.trim() }))
        .filter((link) => link.url.length > 0);

    if (links.length > MAX_LINKS) {
        return {
            data: null,
            isError: true,
            message: `No se pueden agregar más de ${MAX_LINKS} links`,
            status: 400,
        };
    }

    return updateUser(session.authId, session.accessToken, {
        name,
        avatar: httpsAvatar(input.avatar),
        description: input.description?.trim() || null,
    });
}
