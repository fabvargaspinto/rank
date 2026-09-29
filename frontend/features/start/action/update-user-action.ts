"use server";

import { httpsUrlError, MAX_LINKS } from "@/lib/domain-limits";
import {
    updateUser,
    type FetchDataResponse,
    type UserResponse,
} from "@/lib/fetch_data";
import { getAuthSession } from "@/lib/supabase/session";

export type UpdateUserLinkInput = {
    url: string;
};

export type UpdateUserInput = {
    name: string;
    displayName?: string | null;
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
            message: "El usuario es obligatorio",
            status: 400,
            field: "name",
        };
    }

    const links =
        input.links === undefined
            ? undefined
            : input.links
                  .map((link) => ({ url: link.url.trim() }))
                  .filter((link) => link.url.length > 0);

    if (links !== undefined && links.length > MAX_LINKS) {
        return {
            data: null,
            isError: true,
            message: `No se pueden agregar más de ${MAX_LINKS} links`,
            status: 400,
        };
    }

    const linkError = links
        ?.map((link) => httpsUrlError(link.url))
        .find((error) => error != null);

    if (linkError) {
        return {
            data: null,
            isError: true,
            message: linkError,
            status: 400,
        };
    }

    return updateUser(session.accessToken, {
        name,
        ...(input.displayName !== undefined
            ? { display_name: input.displayName?.trim() || null }
            : {}),
        description: input.description?.trim() || null,
        ...(input.avatar !== undefined
            ? { avatar: httpsAvatar(input.avatar) }
            : {}),
        ...(links !== undefined ? { links } : {}),
    });
}
