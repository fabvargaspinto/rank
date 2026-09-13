import { z } from "zod";
import type { FetchDataResponse } from "@/lib/fetch_data";

const emailSchema = z
    .string()
    .trim()
    .min(1, "El email es obligatorio")
    .email("Ingresá un email válido");

export const loginSchema = z.object({
    email: emailSchema,
    password: z.string().min(1, "La contraseña es obligatoria"),
});

export const registerSchema = z
    .object({
        email: emailSchema,
        password: z
            .string()
            .min(1, "La contraseña es obligatoria")
            .min(8, "La contraseña debe tener al menos 8 caracteres")
            .max(64, "La contraseña debe tener menos de 64 caracteres")
            .refine((value) => !/\s/.test(value), {
                message: "La contraseña no debe tener espacios",
            })
            .refine((value) => /\p{L}/u.test(value), {
                message: "La contraseña debe incluir al menos una letra",
            })
            .refine((value) => /\d/.test(value), {
                message: "La contraseña debe incluir al menos un número",
            }),
        passwordConfirmation: z
            .string()
            .min(1, "Confirmá la contraseña"),
    })
    .refine((data) => data.password === data.passwordConfirmation, {
        message: "Las contraseñas no coinciden",
        path: ["passwordConfirmation"],
    });

export function invalidFormResponse(
    error: z.ZodError,
): FetchDataResponse {
    return {
        data: null,
        isError: true,
        message: error.issues[0]?.message ?? "Revisá los datos del formulario",
        status: 400,
    };
}
