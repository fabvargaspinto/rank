import type { ReactNode } from "react";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import styles from "./status-screen.module.css";

type StatusScreenProps = {
    title: string;
    description: string;
    action?: ReactNode;
};

export default function StatusScreen({
    title,
    description,
    action,
}: StatusScreenProps) {
    return (
        <PageWrapper>
            <section className={styles.container}>
                <h1 className={styles.title}>{title}</h1>
                <p className={styles.description}>{description}</p>
                {action ? <div className={styles.action}>{action}</div> : null}
            </section>
        </PageWrapper>
    );
}
