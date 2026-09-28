import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import treeStyles from "@/features/tree/component/tree.module.css";
import styles from "./skeleton.module.css";

export default function TreeSkeleton() {
    return (
        <PageWrapper>
            <article
                className={treeStyles.container}
                aria-busy="true"
                aria-label="Cargando"
            >
                <div className={`${treeStyles.header} ${styles.headerFill}`} />
                <div className={treeStyles.tabs}>
                    <div className={styles.tab} />
                    <div className={styles.tab} />
                </div>
                <div className={`${treeStyles.panel} ${styles.comments}`}>
                    <div className={styles.comment} />
                    <div className={styles.commentShort} />
                    <div className={styles.comment} />
                </div>
            </article>
        </PageWrapper>
    );
}
