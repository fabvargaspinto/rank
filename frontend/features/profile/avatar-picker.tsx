"use client";

import Image from "next/image";
import type { ChangeEvent } from "react";
import Avatar from "@/components/ui/avatar/avatar";
import { AVATAR_ACCEPT } from "@/lib/domain-limits";
import styles from "./avatar-picker.module.css";

type AvatarPickerProps = {
    previewUrl: string;
    fallbackName: string;
    onChange: (event: ChangeEvent<HTMLInputElement>) => void;
    variant: "avatar" | "banner";
    emptyHint?: string;
    changeHint?: string;
    ariaLabelledBy?: string;
};

export default function AvatarPicker({
    previewUrl,
    fallbackName,
    onChange,
    variant,
    emptyHint = "Agregar foto",
    changeHint = "Cambiar foto",
    ariaLabelledBy,
}: AvatarPickerProps) {
    const hint = previewUrl ? changeHint : emptyHint;

    if (variant === "banner") {
        return (
            <label className={styles.bannerPicker}>
                {previewUrl ? (
                    <Image
                        src={previewUrl}
                        alt=""
                        fill
                        unoptimized
                        className={styles.bannerPreview}
                        sizes="100vw"
                    />
                ) : null}
                <input
                    className={styles.fileInput}
                    type="file"
                    accept={AVATAR_ACCEPT}
                    aria-labelledby={ariaLabelledBy}
                    onChange={onChange}
                />
                <span className={styles.bannerHint}>{hint}</span>
            </label>
        );
    }

    return (
        <label className={styles.avatarPicker}>
            <Avatar
                src={previewUrl || null}
                name={fallbackName}
                size="lg"
                className={styles.avatar}
                alt="Vista previa del avatar"
            />
            <input
                className={styles.fileInput}
                type="file"
                accept={AVATAR_ACCEPT}
                onChange={onChange}
            />
            <span className={styles.avatarHint}>{hint}</span>
        </label>
    );
}
