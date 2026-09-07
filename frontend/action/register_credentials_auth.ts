"use server";

import { verifySchema } from "@/lib/verify_schema";
import { fetchAction } from "@/lib/fetch_action";
import { setAuthSession } from "@/lib/auth-session";
import { z } from "zod";
import { ActionResponse } from "./action-response";

const PASSWORD_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

const registerSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(3, { message: "el nombre debe tener al menos 3 caracteres" }),
    email: z
      .string()
      .trim()
      .toLowerCase()
      .pipe(z.email({ message: "email inválido" })),
    password: z
      .string()
      .min(8, { message: "la contraseña debe tener al menos 8 caracteres" })
      .max(72, { message: "la contraseña es demasiado larga" })
      .regex(PASSWORD_REGEX, {
        message:
          "la contraseña debe tener mayúscula, minúscula, número y un carácter especial",
      }),
    confirmPassword: z.string().min(1, {
      message: "confirma la contraseña",
    }),
  })
  .refine((value) => value.password === value.confirmPassword, {
    message: "las contraseñas no coinciden",
    path: ["confirmPassword"],
  });

type RegisterData = {
  session?: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  } | null;
};

export async function registerCredentialsAuth(
  _previousState: ActionResponse<RegisterData>,
  formData: FormData,
): Promise<ActionResponse<RegisterData>> {
  const { error, data } = verifySchema({
    schema: registerSchema,
    data: {
      name: String(formData.get("name") ?? ""),
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? ""),
      confirmPassword: String(formData.get("confirmPassword") ?? ""),
    },
  });

  if (error) {
    return {
      message: error,
      isError: true,
    };
  }

  const result = await fetchAction<RegisterData>({
    path: "/auth/register/credentials",
    body: {
      name: data.name,
      email: data.email,
      password: data.password,
      confirm_password: data.confirmPassword,
    },
    fallbackMessage: "no se pudo registrar la cuenta",
  });

  if (result.isError) {
    return {
      message: toUserMessage(result.message),
      isError: true,
    };
  }

  if (result.data?.session) {
    await setAuthSession(result.data.session);
  }

  return {
    message: "usuario registrado correctamente",
    isError: false,
    data: result.data,
  };
}

function toUserMessage(message: string): string {
  if (/already exists/i.test(message) && /name/i.test(message)) {
    return "el nombre ya está en uso";
  }
  if (/already exists/i.test(message)) {
    return "el email ya está en uso";
  }
  if (/invalid email/i.test(message)) {
    return "email inválido";
  }
  if (/too short/i.test(message)) {
    return "la contraseña debe tener al menos 8 caracteres";
  }
  if (/too long/i.test(message)) {
    return "la contraseña es demasiado larga";
  }
  if (/uppercase|special character|lowercase/i.test(message)) {
    return "la contraseña debe tener mayúscula, minúscula, número y un carácter especial";
  }
  if (/no coinciden|not match|confirme la contraseña/i.test(message)) {
    return "las contraseñas no coinciden";
  }
  return message || "no se pudo registrar la cuenta";
}
