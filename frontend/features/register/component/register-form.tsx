"use client";

import { useActionState } from "react";
import FormHero from "@/components/ui/form-hero/form-hero";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { registerCredentialAction } from "../action/register-credential-action";
import { registerGoogleAction } from "../action/register-google-action";

type RegisterFormProps = {
    initialError?: string;
};

export default function RegisterForm({ initialError = "" }: RegisterFormProps) {
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
            googleAction={registerGoogleAction}
            pending={pending}
            isError={state.isError || Boolean(initialError)}
            message={state.message || initialError}
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input
                type="password"
                name="password"
                placeholder="Password"
                autoComplete="new-password"
            />
            <Input
                type="password"
                name="passwordConfirmation"
                placeholder="Password Confirmation"
                autoComplete="new-password"
            
            />
        </FormHero>
    );
}
