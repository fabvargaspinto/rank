import type { ReactNode } from "react";
import AuthLegalLinks from "@/features/legal/auth-legal-links";
import styles from "./auth-shell.module.css";

export default function AuthShell({ children }: { children: ReactNode }) {
    return (
        <div className={styles.shell}>
            <div className={styles.main}>{children}</div>
            <AuthLegalLinks />
        </div>
    );
}
