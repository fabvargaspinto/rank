"use client";

import { useActionState } from "react";
import FormHero from "@/pages/ui/form-hero/form-hero";
import Input from "@/pages/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { registerCredentialAction } from "../action/register-credential-action";

export default function RegisterForm() {
    const [state, formAction, pending] = useActionState(
        registerCredentialAction,
        emptyFetchResponse,
    );

    return (
        <FormHero
            description="Crea tu cuenta para participar de la comunidad nómada"
            submitLabel="Register"
            footerPrompt="ya tienes una cuenta?"
            footerHref="/"
            footerLabel="Inicia sesión"
            action={formAction}
            pending={pending}
            isError={state.isError}
            message={state.message}
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" />
            <Input type="password" name="passwordConfirmation" placeholder="Password Confirmation" />
        </FormHero>
    );
}
