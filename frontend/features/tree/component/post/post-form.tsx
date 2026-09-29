"use client";

import { useId, useState, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import { createPostAction } from "@/features/tree/action/create-post-action";
import {
    httpsUrlError,
    LINK_MAX_LENGTH,
    POST_TEXT_MAX_LENGTH,
    postTextError,
} from "@/lib/domain-limits";
import type { PostResponse } from "@/lib/fetch_data";
import styles from "./post-form.module.css";

type PostFormProps = {
    onAdd: (post: PostResponse) => void;
};

function normalizeLink(value: string): string | undefined {
    const trimmed = value.trim();

    if (!trimmed) {
        return undefined;
    }

    try {
        return new URL(trimmed).toString();
    } catch {
        try {
            return new URL(`https://${trimmed}`).toString();
        } catch {
            return trimmed;
        }
    }
}

export default function PostForm({ onAdd }: PostFormProps) {
    const textId = useId();
    const linkId = useId();
    const [text, setText] = useState("");
    const [link, setLink] = useState("");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const textError = postTextError(text);

        if (textError) {
            setError(textError);
            return;
        }

        const normalizedLink = normalizeLink(link);
        const linkError = normalizedLink ? httpsUrlError(normalizedLink) : null;

        if (linkError) {
            setError(linkError);
            return;
        }

        setSaving(true);
        setError("");

        const result = await createPostAction({
            text: text.trim(),
            link: normalizedLink,
        });

        setSaving(false);

        if (result.isError || !result.data) {
            setError(result.message || "No se pudo publicar");
            return;
        }

        setText("");
        setLink("");
        onAdd(result.data);
    }

    return (
        <form className={styles.form} onSubmit={onSubmit}>
            <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor={textId}>
                    Publicación
                </label>
                <textarea
                    id={textId}
                    name="text"
                    className={styles.textarea}
                    value={text}
                    maxLength={POST_TEXT_MAX_LENGTH}
                    rows={4}
                    placeholder="Escribí una publicación"
                    required
                    disabled={saving}
                    onChange={(event) => setText(event.target.value)}
                />
            </div>
            <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor={linkId}>
                    Enlace
                </label>
                <Input
                    id={linkId}
                    name="link"
                    type="text"
                    value={link}
                    inputMode="url"
                    autoComplete="url"
                    placeholder="https:// (opcional)"
                    maxLength={LINK_MAX_LENGTH}
                    disabled={saving}
                    onChange={(event) => setLink(event.target.value)}
                />
            </div>
            {error ? <p className={styles.error}>{error}</p> : null}
            <Button type="submit" disabled={saving}>
                {saving ? "Publicando..." : "Publicar"}
            </Button>
        </form>
    );
}
