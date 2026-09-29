"use client";

import { useId, useState, type ChangeEvent, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/button/button";
import Carousel from "@/components/ui/carousel/carousel";
import Input from "@/components/ui/input/input";
import AvatarPicker from "@/features/profile/avatar-picker";
import {
    createEmptyLink,
    firstLinkValidationError,
    linksPayload,
    trimProfileText,
    type ProfileLink,
} from "@/features/profile/model";
import ProfileLinksEditor from "@/features/profile/profile-links-editor";
import { useAvatarUpload } from "@/features/profile/use-avatar-upload";
import { isUsernameFieldError } from "@/lib/api/types";
import {
    DESCRIPTION_MAX_LENGTH,
    DISPLAY_NAME_MAX_LENGTH,
    MAX_LINKS,
    USERNAME_MAX_LENGTH,
    usernameShapeError,
} from "@/lib/domain-limits";
import { checkNameAvailability } from "../action/check-name-action";
import { updateUserAction } from "../action/update-user-action";
import { uploadAvatarAction } from "../action/upload-avatar-action";
import styles from "./start-form.module.css";

const PROFILE_HOST = "sellonomada.com/";
const STEP_COUNT = 3;

export default function StartForm() {
    const router = useRouter();
    const nameId = useId();
    const displayNameId = useId();
    const descriptionId = useId();
    const linksId = useId();
    const [step, setStep] = useState(0);
    const [name, setName] = useState("");
    const [nameError, setNameError] = useState("");
    const [displayName, setDisplayName] = useState("");
    const [displayNameError, setDisplayNameError] = useState("");
    const [checkingName, setCheckingName] = useState(false);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState("");
    const [description, setDescription] = useState("");
    const [links, setLinks] = useState<ProfileLink[]>(() => [
        createEmptyLink("link-0"),
    ]);
    const {
        previewUrl: photo,
        file: photoFile,
        onFileChange,
    } = useAvatarUpload({ initialUrl: "" });

    const trimmedName = trimProfileText(name);
    const savedUsername = trimmedName.toLowerCase();
    const lowercaseHint =
        trimmedName && trimmedName !== savedUsername
            ? `Se guarda en minúsculas: ${savedUsername}`
            : "";
    const canSkip = step > 0;
    const isLast = step === STEP_COUNT - 1;

    function goTo(next: number) {
        setStep(Math.min(Math.max(next, 0), STEP_COUNT - 1));
    }

    function onNameChange(event: ChangeEvent<HTMLInputElement>) {
        setName(event.target.value);
        setNameError("");
    }

    async function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const error = await onFileChange(event);

        if (error) {
            setSaveError(error);
            return;
        }

        setSaveError("");
    }

    async function continueFromName() {
        const username = trimProfileText(name);
        const visibleName = trimProfileText(displayName);

        const shapeError = usernameShapeError(username);

        if (shapeError) {
            setNameError(shapeError);
        }

        if (!visibleName) {
            setDisplayNameError("El nombre es obligatorio");
        }

        if (shapeError || !visibleName) {
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

    async function finish() {
        setSaving(true);
        setSaveError("");

        try {
            const linkError = firstLinkValidationError(links);

            if (linkError) {
                setSaveError(linkError);
                return;
            }

            if (photoFile) {
                const uploaded = await uploadAvatarAction(photoFile);

                if (uploaded.isError || !uploaded.data) {
                    setSaveError(uploaded.message || "No se pudo subir la imagen");
                    return;
                }
            }

            const result = await updateUserAction({
                name: trimmedName,
                displayName: trimProfileText(displayName),
                description: trimProfileText(description),
                links: linksPayload(links),
            });

            if (result.isError) {
                if (isUsernameFieldError(result)) {
                    setNameError(result.message || "Ese usuario no es válido");
                    goTo(0);
                    return;
                }

                if (result.field === "display_name") {
                    setDisplayNameError(result.message || "Ese nombre no es válido");
                    goTo(0);
                    return;
                }

                setSaveError(result.message || "No se pudo guardar tu perfil");
                return;
            }

            router.push("/dashboard/tree");
        } catch {
            setSaveError("No se pudo guardar tu perfil");
        } finally {
            setSaving(false);
        }
    }

    function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (step === 0) {
            void continueFromName();
            return;
        }

        if (isLast) {
            void finish();
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
                            Cómo te presentás
                        </h1>
                        <p className={styles.description}>
                            El nombre es el que se ve en tu perfil. El usuario
                            es la URL y se guarda en minúsculas.
                        </p>
                    </div>
                    <div className={styles.field}>
                        <label className={styles.fieldLabel} htmlFor={nameId}>
                            Usuario
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
                                placeholder="usuario"
                                maxLength={USERNAME_MAX_LENGTH}
                                aria-invalid={Boolean(nameError)}
                                aria-describedby={
                                    [
                                        lowercaseHint ? `${nameId}-hint` : "",
                                        nameError ? `${nameId}-error` : "",
                                    ]
                                        .filter(Boolean)
                                        .join(" ") || undefined
                                }
                                onChange={onNameChange}
                            />
                        </div>
                        {lowercaseHint ? (
                            <p id={`${nameId}-hint`} className={styles.hint}>
                                {lowercaseHint}
                            </p>
                        ) : null}
                        {nameError ? (
                            <p id={`${nameId}-error`} className={styles.error}>
                                {nameError}
                            </p>
                        ) : null}
                    </div>
                    <div className={styles.field}>
                        <label className={styles.fieldLabel} htmlFor={displayNameId}>
                            Nombre
                        </label>
                        <Input
                            id={displayNameId}
                            name="displayName"
                            value={displayName}
                            autoComplete="name"
                            placeholder="Sello Nómada"
                            maxLength={DISPLAY_NAME_MAX_LENGTH}
                            aria-invalid={Boolean(displayNameError)}
                            aria-describedby={`${displayNameId}-hint`}
                            onChange={(event) => {
                                setDisplayName(event.target.value);
                                setDisplayNameError("");
                            }}
                        />
                        <p id={`${displayNameId}-hint`} className={styles.hint}>
                            Así aparece en tu perfil. Podés usar mayúsculas,
                            espacios y emojis.
                        </p>
                        {displayNameError ? (
                            <p className={styles.error}>{displayNameError}</p>
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
                    <AvatarPicker
                        variant="avatar"
                        previewUrl={photo}
                        fallbackName={
                            trimProfileText(displayName) || trimmedName || name
                        }
                        onChange={onPhotoChange}
                    />
                </section>

                <section className={styles.slide} aria-labelledby={descriptionId}>
                    <div className={styles.header}>
                        <h1 className={styles.title}>Sobre vos</h1>
                        <p className={styles.description}>
                            Contá quién sos y dejá los links de tus redes. Podés
                            agregar hasta {MAX_LINKS}.
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
                    <ProfileLinksEditor
                        id={linksId}
                        links={links}
                        onLinksChange={setLinks}
                    />
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

            {saveError ? (
                <p className={styles.error} role="alert">
                    {saveError}
                </p>
            ) : null}

            <div className={styles.actions}>
                <Button
                    type="submit"
                    disabled={
                        checkingName ||
                        saving ||
                        (step === 0 &&
                            (!trimProfileText(name) || !trimProfileText(displayName)))
                    }
                >
                    {checkingName
                        ? "Comprobando..."
                        : saving
                          ? "Guardando..."
                          : isLast
                            ? "Listo"
                            : "Continuar"}
                </Button>
                {canSkip ? (
                    <Button
                        type="button"
                        variant="secondary"
                        disabled={saving}
                        onClick={() => (isLast ? void finish() : goTo(step + 1))}
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
