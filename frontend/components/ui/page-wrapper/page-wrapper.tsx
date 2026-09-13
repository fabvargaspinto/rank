import styles from "./page-wrapper.module.css";

export default function PageWrapper({ children }: { children: React.ReactNode }) {
    return (
        <div className={styles.pageWrapper}>
            {children}
        </div>
    );
}