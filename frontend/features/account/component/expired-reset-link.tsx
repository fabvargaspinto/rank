import Link from "next/link";
import styles from "./expired-reset-link.module.css";

export default function ExpiredResetLink() {
    return (
        <div className={styles.box}>
            <h1 className={styles.title}>El enlace venció</h1>
            <p className={styles.text}>
                Pedí uno nuevo para elegir otra contraseña.
            </p>
            <Link href="/forgot-password">Olvidé mi contraseña</Link>
        </div>
    );
}
