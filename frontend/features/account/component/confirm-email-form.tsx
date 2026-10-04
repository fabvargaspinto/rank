"use client";

import { useActionState } from "react";
import FormHero from "@/components/ui/form-hero/form-hero";
import { emptyFetchResponse } from "@/lib/api/types";
import { confirmEmailAction } from "../action/confirm-email-action";

type ConfirmEmailFormProps = {
    tokenHash: string;
    type: string;
    code: string;
    next: string;
    submitLabel: string;
    description: string;
};

export default function ConfirmEmailForm({
    tokenHash,
    type,
    code,
    next,
    submitLabel,
    description,
}: ConfirmEmailFormProps) {
    const [state, formAction, pending] = useActionState(
        confirmEmailAction,
        emptyFetchResponse,
    );

    return (
        <FormHero
            description={description}
            submitLabel={submitLabel}
            footerPrompt="¿Ya confirmaste?"
            footerHref="/login"
            footerLabel="Iniciá sesión"
            action={formAction}
            pending={pending}
            isError={state.isError}
            message={state.message}
            showGoogle={false}
        >
            {tokenHash ? (
                <input type="hidden" name="token_hash" value={tokenHash} />
            ) : null}
            {type ? <input type="hidden" name="type" value={type} /> : null}
            {code ? <input type="hidden" name="code" value={code} /> : null}
            {next ? <input type="hidden" name="next" value={next} /> : null}
        </FormHero>
    );
}
