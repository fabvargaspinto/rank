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
};

export default function FormHero({
    description,
    children,
    submitLabel,
    footerPrompt,
    footerHref,
    footerLabel,
}: FormHeroProps) {
    return (
        <form className={styles.form}>
            <div className={styles.header}>
                <h1 className={styles.title}>
                    Sello{" "}
                    <span className={styles.titleAccent}>Nomada</span>
                </h1>
                <p className={styles.description}>{description}</p>
            </div>
            <div className={styles.section}>{children}</div>
            <div className={styles.section}>
                <Button type="submit">{submitLabel}</Button>
                <div className={styles.separator} />
                <GoogleButton />
                <p className={styles.footerLink}>
                    {footerPrompt}{" "}
                    <Link href={footerHref}>{footerLabel}</Link>
                </p>
            </div>
        </form>
    );
}
