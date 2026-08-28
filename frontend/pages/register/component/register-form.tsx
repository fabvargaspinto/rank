'use client';

import { useState } from 'react';
import Button from '@/ui/button/button';
import Carousel from '@/ui/carousel/carousel';
import styles from './register-form.module.css';
import Link from 'next/link';
import Input from '@/ui/input/input';

function GoogleIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
            <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.3 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 8 3.1l5.7-5.7C34.2 6.1 29.4 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.2-.1-2.3-.4-3.5z" />
            <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 16 19 12 24 12c3.1 0 5.8 1.2 8 3.1l5.7-5.7C34.2 6.1 29.4 4 24 4 16.3 4 9.6 8.3 6.3 14.7z" />
            <path fill="#4CAF50" d="M24 44c5.2 0 10-2 13.6-5.2l-6.3-5.3C29.2 35.1 26.7 36 24 36c-5.3 0-9.7-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
            <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-1.1 3.2-3.5 5.8-6.6 7.5l6.3 5.3C38.2 37.3 44 31.5 44 24c0-1.2-.1-2.3-.4-3.5z" />
        </svg>
    );
}

export default function RegisterForm() {
    const [step, setStep] = useState(0);
    const [name, setName] = useState('');
    const canContinue = name.trim().length > 0;

    return (
        <section className={styles.register}>
            <div className={styles.registerHeader}>
                <h1 className={styles.registerTitle}>Sello <span className={styles.registerTitleHighlight}>Nomada</span></h1>
                <p className={styles.registerDescription}>Crea tu cuenta para unirte a la comunidad</p>
            </div>
            <Carousel index={step} label="Pasos de registro">
                <RegisterName
                    name={name}
                    onNameChange={setName}
                    canContinue={canContinue}
                    onContinue={() => {
                        if (!canContinue) {
                            return;
                        }
                        setStep(1);
                    }}
                />
                <RegistarData onBack={() => setStep(0)} />
            </Carousel>
        </section>
    );
}

function RegistarData({ onBack }: { onBack: () => void }){
    return (
        <div className={styles.registerStep}>
        <button type="button" className={styles.registerBack} onClick={onBack}>
            <BackIcon />
            Volver
        </button>
        <form className={styles.registerForm}>
            <Input type="email" placeholder="Email" name="email" id="email" />
            <Input type="password" placeholder="Password" name="password" id="password" />
            <Input type="password" placeholder="Confirmar password" name="confirmPassword" id="confirmPassword" />
            <div className={styles.registerFeedback}>
            <p className={styles.registerFeedbackText}></p>
            </div>
            <Button variant="primary" size="full">Registrarse</Button>
        </form>
        <div className={styles.registerDivider}>
            <span>o</span>
        </div>

        <div className={styles.registerFormFooter}>
        <Button variant="secondary" size="full">
            <GoogleIcon />
            Registrarse con Google
        </Button>
        <p className={styles.registerFormFooterText}>
            ¿Ya tienes una cuenta?
            <Link href="/" className={styles.registerFormFooterTextLink}>
            &nbsp; Inicia sesión
            </Link>
        </p>
        </div>
        </div>
    );
}

function RegisterName({
    name,
    onNameChange,
    canContinue,
    onContinue,
}: {
    name: string,
    onNameChange: (name: string) => void,
    canContinue: boolean,
    onContinue: () => void,
}){
    return (
        <form
            className={styles.registerForm}
            onSubmit={(event) => {
                event.preventDefault();
                if (!canContinue) {
                    return;
                }
                onContinue();
            }}
        >
        <p id="name-hint" className={styles.nameDescription}>
            El nombre debe ser único, porque es como te pueden encontrar a través de Sello Nomada.
         </p>
           

                <label htmlFor="name" className={styles.nameInput}>
                    <span className={styles.namePrefix} aria-hidden="true">sellonamada.cl/&nbsp;</span>
                    <input
                        type="text"
                        name="name"
                        id="name"
                        value={name}
                        onChange={(event) => onNameChange(event.target.value)}
                        placeholder="tu nombre"
                        className={styles.nameValue}
                        aria-label="Nombre"
                        aria-describedby="name-hint"
                        autoComplete="username"
                        autoCapitalize="none"
                        autoCorrect="off"
                        spellCheck={false}
                        required
                    />
                </label>
            <div className={styles.registerFeedback}>
            <p className={styles.registerFeedbackText}></p>
            </div>
           
            <Button variant="primary" size="full" onClick={onContinue} disabled={!canContinue}>Continuar</Button>
        </form>
    );
}

function BackIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M10 3.5 5.5 8 10 12.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}
