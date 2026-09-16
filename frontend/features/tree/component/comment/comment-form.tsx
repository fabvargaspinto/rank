"use client";

import { useId, useState, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import styles from "./comment-form.module.css";

export type CommentDraft = {
    text: string;
    link?: string;
};

type CommentFormProps = {
    onAdd: (comment: CommentDraft) => void;
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

    function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const nextText = text.trim();

        if (!nextText) {
            return;
        }

        onAdd({
            text: nextText,
            link: normalizeLink(link),
        });
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
                    onChange={(event) => setLink(event.target.value)}
                />
            </div>
            <Button type="submit">Publicar</Button>
        </form>
    );
}
