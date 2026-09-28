"use client";

import { useActionState } from "react";
import FormHero from "@/components/ui/form-hero/form-hero";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { resetPasswordAction } from "../action/reset-password-action";

export default function ResetPasswordForm() {
    const [state, formAction, pending] = useActionState(
        resetPasswordAction,
        emptyFetchResponse,
    );

    return (
        <FormHero
            description="Elegí una contraseña nueva"
            submitLabel="Guardar contraseña"
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
                type="password"
                name="password"
                placeholder="Contraseña"
                autoComplete="new-password"
            />
            <Input
                type="password"
                name="passwordConfirmation"
                placeholder="Confirmá la contraseña"
                autoComplete="new-password"
            />
        </FormHero>
    );
}
