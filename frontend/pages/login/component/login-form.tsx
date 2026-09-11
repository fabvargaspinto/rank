"use client";

import { useActionState } from "react";
import FormHero from "@/pages/ui/form-hero/form-hero";
import Input from "@/pages/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { loginCredentialAction } from "../action/login-credential-action";

export default function LoginForm() {
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
            pending={pending}
            isError={state.isError}
            message={state.message}
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" autoComplete="current-password" />
        </FormHero>
    );
}
