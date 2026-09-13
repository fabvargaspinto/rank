"use client";

import { useActionState } from "react";
import FormHero from "@/components/ui/form-hero/form-hero";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { loginCredentialAction } from "../action/login-credential-action";
import { loginGoogleAction } from "../action/login-google-action";

type LoginFormProps = {
    initialError?: string;
};

export default function LoginForm({ initialError = "" }: LoginFormProps) {
    const [state, formAction, pending] = useActionState(
        loginCredentialAction,
        emptyFetchResponse,
    );

    return (
        <FormHero
            description="Comunidad para musicos, astistas y creadores de contenido"
            submitLabel="Login"
            footerPrompt="no tienes una cuenta?"
            footerHref="/register"
            footerLabel="Registrate"
            action={formAction}
            googleAction={loginGoogleAction}
            pending={pending}
            isError={state.isError || Boolean(initialError)}
            message={state.message || initialError}
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" autoComplete="current-password" />
        </FormHero>
    );
}
