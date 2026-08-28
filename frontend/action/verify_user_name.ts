import { verifySchema } from "@/lib/verify_schema";
import { z } from "zod";
import { ActionResponse } from "./action-response";


const MIN_USERNAME_LENGTH = 3;
const MAX_USERNAME_LENGTH = 32;

const nameSchema = z
  .string()
  .trim()
  // mínimo 3 caracteres
  .min(MIN_USERNAME_LENGTH, {
    message: "el nombre debe tener al menos 3 caracteres",
  })
  // máximo 32 caracteres
  .max(MAX_USERNAME_LENGTH, {
    message: "el nombre debe tener a lo sumo 32 caracteres",
  })
  // no puede contener espacios
  .refine((value) => !/\s/.test(value), {
    message: "el nombre no puede contener espacios",
  })
  // solo letras, números, guiones y guiones bajos
  .regex(/^[a-zA-Z0-9-_]+$/, {
    message: "el nombre debe contener solo letras, números, guiones y guiones bajos",
  });


export async function verifyUserName(
    _previousState: ActionResponse<void>,
    formData: FormData,
): Promise<ActionResponse<void>> {
    const name = String(formData.get("name") ?? "");
    const { error, data } = verifySchema({ schema: nameSchema, data: name });
    if (error) {
        return {
            message: error,
            isError: true,
        };
    }

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/verify-name`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name: data }),
        });

        const payload = await response.json().catch(() => null);
        const message = typeof payload?.message === "string"
            ? payload.message
            : response.statusText;

        if (!response.ok || payload?.isError) {
            return {
                message: toUserMessage(message),
                isError: true,
            };
        }

        return {
            message: "nombre verificado correctamente",
            isError: false,
        };
    } catch {
        return {
            message: "no se pudo verificar el nombre",
            isError: true,
        };
    }
}

function toUserMessage(message: string): string {
    if (/already exists/i.test(message)) {
        return "el nombre ya está en uso";
    }
    if (/too short/i.test(message)) {
        return "el nombre debe tener al menos 3 caracteres";
    }
    if (/too long/i.test(message)) {
        return "el nombre debe tener a lo sumo 32 caracteres";
    }
    if (/cannot contain spaces/i.test(message)) {
        return "el nombre no puede contener espacios";
    }
    if (/invalid characters/i.test(message)) {
        return "el nombre debe contener solo letras, números, guiones y guiones bajos";
    }
    return message || "no se pudo verificar el nombre";
}
