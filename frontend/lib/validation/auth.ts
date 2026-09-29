import { z } from "zod";
import { PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH } from "@/lib/domain-limits";
import type { FetchDataResponse } from "@/lib/api/types";

const emailSchema = z
    .string()
    .trim()
    .min(1, "El email es obligatorio")
    .email("Ingresá un email válido");

export const loginSchema = z.object({
    email: emailSchema,
    password: z.string().min(1, "La contraseña es obligatoria"),
});

export const passwordSchema = z
    .string()
    .min(1, "La contraseña es obligatoria")
    .min(
        PASSWORD_MIN_LENGTH,
        `La contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres`,
    )
    .max(
        PASSWORD_MAX_LENGTH,
        `La contraseña no puede superar ${PASSWORD_MAX_LENGTH} caracteres`,
    )
    .refine((value) => /\d/.test(value), {
        message: "La contraseña debe incluir al menos un número",
    })
    .refine((value) => /[A-Z]/.test(value), {
        message: "La contraseña debe incluir al menos una letra mayúscula",
    })
    .refine((value) => /[a-z]/.test(value), {
        message: "La contraseña debe incluir al menos una letra minúscula",
    });

const passwordConfirmationSchema = z
    .string()
    .min(1, "Confirmá la contraseña");

export const registerSchema = z
    .object({
        email: emailSchema,
        password: passwordSchema,
        passwordConfirmation: passwordConfirmationSchema,
    })
    .refine((data) => data.password === data.passwordConfirmation, {
        message: "Las contraseñas no coinciden",
        path: ["passwordConfirmation"],
    });

export const resetPasswordSchema = z
    .object({
        password: passwordSchema,
        passwordConfirmation: passwordConfirmationSchema,
    })
    .refine((data) => data.password === data.passwordConfirmation, {
        message: "Las contraseñas no coinciden",
        path: ["passwordConfirmation"],
    });

export { emailSchema };

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
