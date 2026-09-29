"use client";

import { useActionState } from "react";
import FormHero from "@/components/ui/form-hero/form-hero";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/api/types";
import { forgotPasswordAction } from "../action/forgot-password-action";

export default function ForgotPasswordForm() {
    const [state, formAction, pending] = useActionState(
        forgotPasswordAction,
        emptyFetchResponse,
    );

    return (
        <FormHero
            description="Te enviamos un enlace para elegir una contraseña nueva"
            submitLabel="Enviar enlace"
            footerPrompt="¿Recordaste la contraseña?"
            footerHref="/login"
            footerLabel="Iniciá sesión"
            action={formAction}
            pending={pending}
            isError={state.isError}
            message={state.message}
            showGoogle={false}
        >
            <Input
                type="email"
                name="email"
                placeholder="Email"
                autoComplete="email"
            />
        </FormHero>
    );
}
