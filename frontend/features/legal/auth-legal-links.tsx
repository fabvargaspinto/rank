import Link from "next/link";
import styles from "./auth-legal-links.module.css";

export default function AuthLegalLinks() {
    return (
        <p className={styles.links}>
            Al continuar aceptas los{" "}
            <Link href="/terminos">Términos</Link> y la{" "}
            <Link href="/privacidad">Privacidad</Link>.
        </p>
    );
}
