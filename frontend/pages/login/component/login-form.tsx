import Button from "@/pages/ui/button/button";
import GoogleButton from "@/pages/ui/google-button/google-button";
import Input from "@/pages/ui/input/input";
import styles from "./login-form.module.css";
import Link from "next/link";

export default function LoginForm() {
    return (
        <form className={styles.loginForm}>
            <LoginFormHeader />
            <LoginFormBody />
        </form>
    );
}

function LoginFormHeader() {
    return (
        <div className={styles.loginFormHeader}>
            <h1 className={styles.loginFormHeaderTitle}>
                Sello{" "}
                <span className={styles.loginFormHeaderTitleAccent}>
                Nomada
                </span>
            </h1>
            <p className={styles.loginFormHeaderDescription}>
                crea tu cuenta para participar de la comunidad nómada
                </p>
        </div>
    );
}

function LoginFormBody() {
    return (
        <>
 
        <div className={styles.loginFormBody}>
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password"  />
        </div>
        <div className={styles.loginFormBody}>
            <Button type="submit">Login</Button>
            <div className={styles.loginFormBodySeparator}></div>
            <GoogleButton />
            <p className={styles.loginFormFooterLink}>no tienes una cuenta? <Link href="/register">Registrate</Link></p>
        </div>
        </>
    );
}