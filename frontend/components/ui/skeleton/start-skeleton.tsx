import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import formStyles from "@/features/start/component/start-form.module.css";
import styles from "./skeleton.module.css";

export default function StartSkeleton() {
    return (
        <PageWrapper>
            <div className={formStyles.form} aria-busy="true" aria-label="Cargando">
                <section className={formStyles.slide}>
                    <div className={formStyles.header}>
                        <div className={styles.title} />
                        <div className={styles.line} />
                        <div className={styles.line} />
                    </div>
                    <div className={styles.field} />
                    <div className={styles.field} />
                </section>
                <div className={formStyles.dots} aria-hidden="true">
                    <span className={`${formStyles.dot} ${formStyles.dotActive}`} />
                    <span className={formStyles.dot} />
                    <span className={formStyles.dot} />
                </div>
                <div className={formStyles.actions}>
                    <div className={styles.button} />
                </div>
            </div>
        </PageWrapper>
    );
}
