import type { ReactNode } from "react";
import Link from "next/link";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import styles from "./legal-document.module.css";

type LegalDocumentProps = {
    title: string;
    updatedAt: string;
    children: ReactNode;
};

export default function LegalDocument({
    title,
    updatedAt,
    children,
}: LegalDocumentProps) {
    return (
        <PageWrapper>
            <article className={styles.document}>
                <p className={styles.brand}>
                    <Link href="/">Sello Nómada</Link>
                </p>
                <h1 className={styles.title}>{title}</h1>
                <p className={styles.updated}>Última actualización: {updatedAt}</p>
                <div className={styles.body}>{children}</div>
                <nav className={styles.nav} aria-label="Documentos legales">
                    <Link href="/privacidad">Privacidad</Link>
                    <Link href="/terminos">Términos</Link>
                    <Link href="/register">Crear cuenta</Link>
                </nav>
            </article>
        </PageWrapper>
    );
}
