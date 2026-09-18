"use server";

import { fetchUserByName } from "@/lib/fetch_data";

export type NameAvailability = {
    available: boolean;
    message: string;
};

export async function checkNameAvailability(
    name: string,
): Promise<NameAvailability> {
    const username = name.trim().toLowerCase();

    if (!username) {
        return {
            available: false,
            message: "El nombre es obligatorio",
        };
    }

    const result = await fetchUserByName(username);

    if (result.status === 404) {
        return {
            available: true,
            message: "",
        };
    }

    if (result.isError) {
        return {
            available: false,
            message: result.message || "No se pudo comprobar el nombre",
        };
    }

    return {
        available: false,
        message: "Ese nombre ya está en uso",
    };
}
