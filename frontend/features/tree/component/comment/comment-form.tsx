"use client";

import { useId, useState, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import { createCommentAction } from "@/features/tree/action/create-comment-action";
import type { CommentResponse } from "@/lib/fetch_data";
import styles from "./comment-form.module.css";

type CommentFormProps = {
    onAdd: (comment: CommentResponse) => void;
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

export default function CommentForm({ onAdd }: CommentFormProps) {
    const textId = useId();
    const linkId = useId();
    const [text, setText] = useState("");
    const [link, setLink] = useState("");
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const nextText = text.trim();

        if (!nextText) {
            setError("El comentario es obligatorio");
            return;
        }

        setSaving(true);
        setError("");

        const result = await createCommentAction({
            text: nextText,
            link: normalizeLink(link),
        });

        setSaving(false);

        if (result.isError || !result.data) {
            setError(result.message || "No se pudo publicar el comentario");
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
                    Comentario
                </label>
                <textarea
                    id={textId}
                    name="text"
                    className={styles.textarea}
                    value={text}
                    maxLength={280}
                    rows={4}
                    placeholder="Escribe un comentario"
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
