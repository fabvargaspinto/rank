"use server";

import { z } from "zod";
import { fetchAction } from "@/lib/fetch_action";
import { setAuthSession } from "@/lib/auth-session";
import { verifySchema } from "@/lib/verify_schema";
import { ActionResponse } from "./action-response";

const loginSchema = z.object({
  email: z
    .string()
    .trim()
    .toLowerCase()
    .pipe(z.email({ message: "email inválido" })),
  password: z.string().min(1, { message: "ingresa la contraseña" }),
});

type LoginData = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
};

export async function loginAuth(
  _previousState: ActionResponse<LoginData>,
  formData: FormData,
): Promise<ActionResponse<LoginData>> {
  const { error, data } = verifySchema({
    schema: loginSchema,
    data: {
      email: String(formData.get("email") ?? ""),
      password: String(formData.get("password") ?? ""),
    },
  });

  if (error) {
    return {
      message: error,
      isError: true,
    };
  }

  const result = await fetchAction<LoginData>({
    path: "/auth/login",
    body: {
      email: data.email,
      password: data.password,
    },
    fallbackMessage: "no se pudo iniciar sesión",
  });

  if (result.isError || !result.data) {
    return {
      message: toUserMessage(result.message),
      isError: true,
    };
  }

  await setAuthSession(result.data);

  return {
    message: "sesión iniciada correctamente",
    isError: false,
    data: result.data,
  };
}

function toUserMessage(message: string): string {
  if (/invalid email or password/i.test(message)) {
    return "email o contraseña incorrectos";
  }
  if (/invalid email/i.test(message)) {
    return "email inválido";
  }
  return message || "no se pudo iniciar sesión";
}
