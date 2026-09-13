"use client";

import { useState, type ComponentProps } from "react";
import styles from "./input.module.css";

type InputProps = ComponentProps<"input">;

function EyeIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z" />
            <circle cx="12" cy="12" r="3" />
        </svg>
    );
}

function EyeOffIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M3 3l18 18" />
            <path d="M10.6 10.6A3 3 0 0 0 12 15a3 3 0 0 0 2.4-4.4" />
            <path d="M9.9 5.1A11 11 0 0 1 12 5c6.5 0 10 7 10 7a18 18 0 0 1-3.2 4.4" />
            <path d="M6.6 6.6C4 8.6 2 12 2 12s3.5 7 10 7c1.3 0 2.5-.2 3.6-.6" />
        </svg>
    );
}

export default function Input({ className, type = "text", ...props }: InputProps) {
    const [visible, setVisible] = useState(false);
    const isPassword = type === "password";

    if (!isPassword) {
        return (
            <input
                className={[styles.input, className].filter(Boolean).join(" ")}
                type={type}
                {...props}
            />
        );
    }

    return (
        <div className={styles.passwordField}>
            <input
                className={[styles.input, styles.inputWithToggle, className]
                    .filter(Boolean)
                    .join(" ")}
                type={visible ? "text" : "password"}
                {...props}
            />
            <button
                type="button"
                className={styles.toggle}
                onClick={() => setVisible((current) => !current)}
                aria-label={visible ? "Ocultar contraseña" : "Mostrar contraseña"}
                aria-pressed={visible}
            >
                {visible ? <EyeOffIcon /> : <EyeIcon />}
            </button>
        </div>
    );
}
