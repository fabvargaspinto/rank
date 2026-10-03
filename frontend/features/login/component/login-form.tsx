"use client";

import { useActionState } from "react";
import Link from "next/link";
import FormHero from "@/components/ui/form-hero/form-hero";
import HcaptchaField, {
    hcaptchaSiteKeyFromEnv,
} from "@/components/ui/hcaptcha/hcaptcha-field";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/api/types";
import { loginCredentialAction } from "../action/login-credential-action";
import { loginGoogleAction } from "../action/login-google-action";
import styles from "./login-form.module.css";

type LoginFormProps = {
    initialError?: string;
};

export default function LoginForm({ initialError = "" }: LoginFormProps) {
    const [state, formAction, pending] = useActionState(
        loginCredentialAction,
        emptyFetchResponse,
    );
    const hcaptchaSiteKey = hcaptchaSiteKeyFromEnv();

    return (
        <FormHero
            description="Comunidad para músicos, artistas y creadores de contenido"
            submitLabel="Iniciar sesión"
            footerPrompt="¿No tenés una cuenta?"
            footerHref="/register"
            footerLabel="Registrate"
            action={formAction}
            googleAction={loginGoogleAction}
            pending={pending}
            isError={state.isError || Boolean(initialError && !state.message)}
            message={state.message || initialError}
        >
            <Input
                type="email"
                name="email"
                placeholder="Email"
                aria-label="Email"
                autoComplete="email"
            />
            <Input
                type="password"
                name="password"
                placeholder="Contraseña"
                aria-label="Contraseña"
                autoComplete="current-password"
            />
            <p className={styles.forgot}>
                <Link href="/forgot-password">Olvidé mi contraseña</Link>
            </p>
            {state.code === "email_not_confirmed" ? (
                <p className={styles.resend}>
                    <button
                        type="submit"
                        name="intent"
                        value="resend"
                        disabled={pending}
                    >
                        Reenviar email de confirmación
                    </button>
                </p>
            ) : null}
            {hcaptchaSiteKey ? (
                <HcaptchaField
                    siteKey={hcaptchaSiteKey}
                    resetSignal={`${pending}:${state.message}:${state.code ?? ""}`}
                />
            ) : null}
        </FormHero>
    );
}
