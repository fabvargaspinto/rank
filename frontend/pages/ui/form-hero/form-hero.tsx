import type { ReactNode } from "react";
import Link from "next/link";
import Button from "../button/button";
import GoogleButton from "../google-button/google-button";
import styles from "./form-hero.module.css";

type FormHeroProps = {
    description: string;
    children: ReactNode;
    submitLabel: string;
    footerPrompt: string;
    footerHref: string;
    footerLabel: string;
    action?: (formData: FormData) => void | Promise<void>;
    pending?: boolean;
    isError?: boolean;
    message?: string;
};

export default function FormHero({
    description,
    children,
    submitLabel,
    footerPrompt,
    footerHref,
    footerLabel,
    action,
    pending = false,
    isError = false,
    message = "",
}: FormHeroProps) {
    return (
        <form className={styles.form} action={action}>
            <div className={styles.header}>
                <h1 className={styles.title}>
                    Sello{" "}
                    <span className={styles.titleAccent}>Nomada</span>
                </h1>
                <p className={styles.description}>{description}</p>
            </div>
            <div className={styles.section}>{children}</div>
            {pending || message ? (
                <p className={isError ? styles.messageError : styles.messageOk}>
                    {pending ? "Cargando..." : message}
                </p>
            ) : null}
            <div className={styles.section}>
                <Button type="submit" disabled={pending}>
                    {pending ? "Cargando..." : submitLabel}
                </Button>
                <div className={styles.separator} />
                <GoogleButton disabled={pending} />
                <p className={styles.footerLink}>
                    {footerPrompt}{" "}
                    <Link href={footerHref}>{footerLabel}</Link>
                </p>
            </div>
        </form>
    );
}
