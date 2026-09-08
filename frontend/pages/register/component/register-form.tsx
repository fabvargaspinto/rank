import Input from "@/pages/ui/input/input";
import styles from "./register-form.module.css";

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
                crea tu cuenta para participar de la comunidad nómada
                </p>
        </div>
    );
}

function RegisterFormBody() {
    return (
        <div className={styles.registerFormBody}>
            <Input type="text" name="username" placeholder="Username" autoComplete="username" />
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" autoComplete="new-password" />
            <button type="submit">Register</button>
        </div>
    );
}