import Button from "@/pages/ui/button/button";
import GoogleButton from "@/pages/ui/google-button/google-button";
import Input from "@/pages/ui/input/input";
import styles from "./register-form.module.css";
import Link from "next/link";

export default function RegisterForm() {
    return (
        <form className={styles.registerForm}>
            <RegisterFormHeader />
            <RegisterFormBody />
        </form>
    );
}

function RegisterFormHeader() {
    return (
        <div className={styles.registerFormHeader}>
            <h1 className={styles.registerFormHeaderTitle}>
                Sello{" "}
                <span className={styles.registerFormHeaderTitleAccent}>
                Nomada
                </span>
            </h1>
            <p className={styles.registerFormHeaderDescription}>
                Comunidad para musicos, astistas y creadores de contenido
                </p>
        </div>
    );
}

function RegisterFormBody() {
    return (
        <>
        <div className={styles.registerFormBody}>
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password"  />
            <Input type="password" name="passwordConfirmation" placeholder="Password Confirmation"  />
        </div>
        <div className={styles.registerFormBody}>
            <Button type="submit">Register</Button>
            <div className={styles.registerFormBodySeparator}></div>
            <GoogleButton />
            <p className={styles.registerFormFooterLink}>ya tienes una cuenta? <Link href="/">Inicia sesión</Link></p>
        </div>
        </>
    );
}