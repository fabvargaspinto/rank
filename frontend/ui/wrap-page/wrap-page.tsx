import styles from './wrap-page.module.css';

type screenSize = "full" | "container";

const screenSizeClass = {
    full: styles.full,
    container: styles.container,
}

export default function WrapPage({ children, screenSize = "full" }: { children: React.ReactNode, screenSize?: screenSize }) {
    return (
        <main className={styles.main}>
            <div className={`${styles.content} ${screenSizeClass[screenSize]}`}>
                {children}
            </div>
        </main>
    );
}