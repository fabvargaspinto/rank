"use client";

import { useState } from "react";
import styles from "./avatar.module.css";

type AvatarSize = "sm" | "md" | "lg";

type AvatarProps = {
    src?: string | null;
    alt?: string;
    name?: string | null;
    size?: AvatarSize;
    className?: string;
};

function initialsFromName(name?: string | null): string {
    if (!name) {
        return "";
    }

    const parts = name.trim().split(/\s+/).filter(Boolean);

    if (parts.length === 0) {
        return "";
    }

    if (parts.length === 1) {
        return parts[0].slice(0, 2).toUpperCase();
    }

    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

function UserIcon() {
    return (
        <svg
            className={styles.icon}
            viewBox="0 0 24 24"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c1.6-3.5 4.5-5 8-5s6.4 1.5 8 5" />
        </svg>
    );
}

export default function Avatar({
    src,
    alt,
    name,
    size = "md",
    className,
}: AvatarProps) {
    const [failedSrc, setFailedSrc] = useState<string | null>(null);
    const showImage = Boolean(src) && src !== failedSrc;
    const initials = initialsFromName(name);
    const label = alt?.trim() || name?.trim() || "Avatar";

    return (
        <span
            className={[styles.avatar, styles[size], className].filter(Boolean).join(" ")}
            role="img"
            aria-label={label}
        >
            <span className={styles.fallback} aria-hidden="true">
                {initials || <UserIcon />}
            </span>
            {showImage ? (
                <img
                    className={styles.image}
                    src={src ?? undefined}
                    alt=""
                    draggable={false}
                    referrerPolicy="no-referrer"
                    ref={(node) => {
                        if (!node || !src) {
                            return;
                        }

                        if (node.complete && node.naturalWidth === 0) {
                            queueMicrotask(() => setFailedSrc(src));
                        }
                    }}
                    onError={() => {
                        if (src) {
                            setFailedSrc(src);
                        }
                    }}
                />
            ) : null}
        </span>
    );
}
