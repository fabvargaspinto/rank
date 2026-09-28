import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import formStyles from "@/components/ui/form-hero/form-hero.module.css";
import styles from "./skeleton.module.css";

type FormSkeletonProps = {
    fields: number;
    showGoogle?: boolean;
};

export default function FormSkeleton({
    fields,
    showGoogle = false,
}: FormSkeletonProps) {
    return (
        <PageWrapper>
            <div className={formStyles.form} aria-busy="true" aria-label="Cargando">
                <div className={formStyles.header}>
                    <div className={styles.title} />
                    <div className={styles.line} />
                </div>
                <div className={formStyles.section}>
                    {Array.from({ length: fields }, (_, index) => (
                        <div key={index} className={styles.field} />
                    ))}
                </div>
                <div className={formStyles.section}>
                    <div className={styles.button} />
                    {showGoogle ? (
                        <>
                            <div className={formStyles.separator} />
                            <div className={styles.button} />
                        </>
                    ) : null}
                    <div className={styles.footer} />
                </div>
            </div>
        </PageWrapper>
    );
}
