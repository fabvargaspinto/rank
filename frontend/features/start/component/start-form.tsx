"use client";

import {
    useEffect,
    useId,
    useRef,
    useState,
    type ChangeEvent,
    type FormEvent,
} from "react";
import { useRouter } from "next/navigation";
import Avatar from "@/components/ui/avatar/avatar";
import Button from "@/components/ui/button/button";
import Carousel from "@/components/ui/carousel/carousel";
import Input from "@/components/ui/input/input";
import { checkNameAvailability } from "../action/check-name-action";
import styles from "./start-form.module.css";

const NAME_MAX_LENGTH = 50;
const DESCRIPTION_MAX_LENGTH = 250;
const PROFILE_HOST = "sellonomada.com/";
const STEP_COUNT = 3;

function sanitizeName(value: string) {
    return value
        .toLowerCase()
        .replace(/\s+/g, "")
        .replace(/[^a-z0-9._-]/g, "")
        .slice(0, NAME_MAX_LENGTH);
}

function isObjectUrl(value: string) {
    return value.startsWith("blob:") || value.startsWith("data:");
}

function PlusIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
        >
            <path d="M12 5v14M5 12h14" />
        </svg>
    );
}

export default function StartForm() {
    const router = useRouter();
    const nameId = useId();
    const descriptionId = useId();
    const [step, setStep] = useState(0);
    const [name, setName] = useState("");
    const [nameError, setNameError] = useState("");
    const [checkingName, setCheckingName] = useState(false);
    const [photo, setPhoto] = useState("");
    const [description, setDescription] = useState("");
    const [socials, setSocials] = useState([""]);
    const photoRef = useRef(photo);

    photoRef.current = photo;

    useEffect(() => {
        return () => {
            if (isObjectUrl(photoRef.current)) {
                URL.revokeObjectURL(photoRef.current);
            }
        };
    }, []);

    const canSkip = step > 0;
    const isLast = step === STEP_COUNT - 1;

    function goTo(next: number) {
        setStep(Math.min(Math.max(next, 0), STEP_COUNT - 1));
    }

    function onNameChange(event: ChangeEvent<HTMLInputElement>) {
        setName(sanitizeName(event.target.value));
        setNameError("");
    }

    function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];

        if (!file || !file.type.startsWith("image/")) {
            return;
        }

        const url = URL.createObjectURL(file);

        setPhoto((current) => {
            if (isObjectUrl(current)) {
                URL.revokeObjectURL(current);
            }

            return url;
        });
    }

    function addSocial() {
        setSocials((current) => [...current, ""]);
    }

    function updateSocial(index: number, value: string) {
        setSocials((current) =>
            current.map((item, itemIndex) =>
                itemIndex === index ? value : item,
            ),
        );
    }

    async function continueFromName() {
        const username = name.trim();

        if (!username) {
            setNameError("El nombre es obligatorio");
            return;
        }

        setCheckingName(true);
        const result = await checkNameAvailability(username);
        setCheckingName(false);

        if (!result.available) {
            setNameError(result.message);
            return;
        }

        goTo(1);
    }

    function finish() {
        router.push("/dashboard");
    }

    function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (step === 0) {
            void continueFromName();
            return;
        }

        if (isLast) {
            finish();
            return;
        }

        goTo(step + 1);
    }

    return (
        <form className={styles.form} onSubmit={onSubmit}>
            <Carousel index={step} label="Registro de perfil">
                <section className={styles.slide} aria-labelledby={`${nameId}-title`}>
                    <div className={styles.header}>
                        <h1 id={`${nameId}-title`} className={styles.title}>
                            Elegí tu nombre
                        </h1>
                        <p className={styles.description}>
                            Tiene que ser único: es la URL de tu perfil y no se
                            puede repetir.
                        </p>
                    </div>
                    <div className={styles.field}>
                        <label className={styles.fieldLabel} htmlFor={nameId}>
                            Nombre
                        </label>
                        <div className={styles.urlField}>
                            <span className={styles.urlPrefix}>{PROFILE_HOST}</span>
                            <Input
                                id={nameId}
                                name="name"
                                value={name}
                                className={styles.urlInput}
                                autoComplete="username"
                                spellCheck={false}
                                maxLength={NAME_MAX_LENGTH}
                                placeholder="nombre"
                                aria-invalid={Boolean(nameError)}
                                aria-describedby={
                                    nameError ? `${nameId}-error` : undefined
                                }
                                onChange={onNameChange}
                            />
                        </div>
                        {nameError ? (
                            <p id={`${nameId}-error`} className={styles.error}>
                                {nameError}
                            </p>
                        ) : null}
                    </div>
                </section>

                <section className={styles.slide} aria-label="Foto de avatar">
                    <div className={styles.header}>
                        <h1 className={styles.title}>Tu foto</h1>
                        <p className={styles.description}>
                            Agregá un avatar para que te reconozcan. Podés
                            saltarlo y hacerlo después.
                        </p>
                    </div>
                    <label className={styles.avatarPicker}>
                        <Avatar
                            src={photo || null}
                            name={name}
                            size="lg"
                            className={styles.avatar}
                            alt="Vista previa del avatar"
                        />
                        <input
                            className={styles.fileInput}
                            type="file"
                            accept="image/*"
                            onChange={onPhotoChange}
                        />
                        <span className={styles.avatarHint}>
                            {photo ? "Cambiar foto" : "Agregar foto"}
                        </span>
                    </label>
                </section>

                <section className={styles.slide} aria-labelledby={descriptionId}>
                    <div className={styles.header}>
                        <h1 className={styles.title}>Sobre vos</h1>
                        <p className={styles.description}>
                            Contá quién sos y dejá los links de tus redes. Podés
                            agregar tantos como quieras.
                        </p>
                    </div>
                    <div className={styles.field}>
                        <label className={styles.fieldLabel} htmlFor={descriptionId}>
                            Descripción
                        </label>
                        <textarea
                            id={descriptionId}
                            name="description"
                            className={styles.textarea}
                            value={description}
                            maxLength={DESCRIPTION_MAX_LENGTH}
                            rows={4}
                            placeholder="Una línea sobre tu música"
                            onChange={(event) => setDescription(event.target.value)}
                        />
                    </div>
                    <div className={styles.field}>
                        <span className={styles.fieldLabel} id={`${nameId}-socials`}>
                            Redes sociales
                        </span>
                        <ul className={styles.socials} aria-labelledby={`${nameId}-socials`}>
                            {socials.map((social, index) => (
                                <li key={index} className={styles.socialRow}>
                                    <Input
                                        type="url"
                                        inputMode="url"
                                        autoComplete="url"
                                        placeholder="https://instagram.com/tu-perfil"
                                        value={social}
                                        aria-label={`Link de red social ${index + 1}`}
                                        onChange={(event) =>
                                            updateSocial(index, event.target.value)
                                        }
                                    />
                                    {index === socials.length - 1 ? (
                                        <button
                                            type="button"
                                            className={styles.addSocial}
                                            onClick={addSocial}
                                            aria-label="Añadir otro link"
                                        >
                                            <PlusIcon />
                                        </button>
                                    ) : null}
                                </li>
                            ))}
                        </ul>
                    </div>
                </section>
            </Carousel>

            <div className={styles.dots} aria-hidden="true">
                {Array.from({ length: STEP_COUNT }, (_, index) => (
                    <span
                        key={index}
                        className={[
                            styles.dot,
                            index === step ? styles.dotActive : "",
                        ]
                            .filter(Boolean)
                            .join(" ")}
                    />
                ))}
            </div>

            <div className={styles.actions}>
                <Button type="submit" disabled={checkingName || (step === 0 && !name)}>
                    {checkingName ? "Comprobando..." : isLast ? "Listo" : "Continuar"}
                </Button>
                {canSkip ? (
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={() => (isLast ? finish() : goTo(step + 1))}
                    >
                        Saltar
                    </Button>
                ) : null}
                {step > 0 ? (
                    <button
                        type="button"
                        className={styles.back}
                        onClick={() => goTo(step - 1)}
                    >
                        Atrás
                    </button>
                ) : null}
            </div>
        </form>
    );
}
