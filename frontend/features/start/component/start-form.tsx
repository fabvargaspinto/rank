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
import { updateUserAction } from "../action/update-user-action";
import { uploadAvatarAction } from "../action/upload-avatar-action";
import styles from "./start-form.module.css";

const NAME_MAX_LENGTH = 50;
const DESCRIPTION_MAX_LENGTH = 250;
const MAX_LINKS = 6;
const PROFILE_HOST = "sellonomada.com/";
const STEP_COUNT = 3;
const AVATAR_MIME_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

type ProfileLink = {
    id: string;
    url: string;
};

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

function createEmptyLink(): ProfileLink {
    return { id: crypto.randomUUID(), url: "" };
}

export default function StartForm() {
    const router = useRouter();
    const nameId = useId();
    const descriptionId = useId();
    const linksId = useId();
    const [step, setStep] = useState(0);
    const [name, setName] = useState("");
    const [nameError, setNameError] = useState("");
    const [checkingName, setCheckingName] = useState(false);
    const [saving, setSaving] = useState(false);
    const [saveError, setSaveError] = useState("");
    const [photo, setPhoto] = useState("");
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [description, setDescription] = useState("");
    const [links, setLinks] = useState<ProfileLink[]>(() => [createEmptyLink()]);
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
    const canAddLink = links.length < MAX_LINKS;
    const canRemoveLink = links.length > 1;

    function goTo(next: number) {
        setStep(Math.min(Math.max(next, 0), STEP_COUNT - 1));
    }

    function onNameChange(event: ChangeEvent<HTMLInputElement>) {
        setName(sanitizeName(event.target.value));
        setNameError("");
    }

    function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];

        if (!file || !AVATAR_MIME_TYPES.has(file.type)) {
            return;
        }

        const url = URL.createObjectURL(file);
        setPhotoFile(file);

        setPhoto((current) => {
            if (isObjectUrl(current)) {
                URL.revokeObjectURL(current);
            }

            return url;
        });
    }

    function onLinkChange(id: string, url: string) {
        setLinks((current) =>
            current.map((link) => (link.id === id ? { ...link, url } : link)),
        );
    }

    function addLink() {
        setLinks((current) => {
            if (current.length >= MAX_LINKS) {
                return current;
            }

            return [...current, createEmptyLink()];
        });
    }

    function removeLink(id: string) {
        setLinks((current) => {
            if (current.length <= 1) {
                return current;
            }

            return current.filter((link) => link.id !== id);
        });
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

    async function finish() {
        setSaving(true);
        setSaveError("");

        const nextLinks = links
            .map((link) => ({ url: link.url.trim() }))
            .filter((link) => link.url.length > 0)
            .slice(0, MAX_LINKS);

        let avatar: string | null = null;

        if (photoFile) {
            const uploaded = await uploadAvatarAction(photoFile);

            if (uploaded.isError || !uploaded.data) {
                setSaving(false);
                setSaveError(uploaded.message || "No se pudo subir la imagen");
                return;
            }

            avatar = uploaded.data;
        }

        const result = await updateUserAction({
            name,
            avatar,
            description,
            links: nextLinks,
        });

        setSaving(false);

        if (result.isError) {
            setSaveError(result.message || "No se pudo guardar tu perfil");
            return;
        }

        router.push("/dashboard/tree");
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
                            accept="image/jpeg,image/png,image/webp"
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
                    <div className={styles.field}>
                        <div className={styles.linksHeader}>
                            <span className={styles.fieldLabel} id={linksId}>
                                Links
                            </span>
                            <span className={styles.linksCounter} aria-live="polite">
                                {links.length}/{MAX_LINKS}
                            </span>
                        </div>
                        <ul className={styles.linksList} aria-labelledby={linksId}>
                            {links.map((link, index) => {
                                const inputId = `${linksId}-${link.id}`;

                                return (
                                    <li key={link.id} className={styles.linkRow}>
                                        <Input
                                            id={inputId}
                                            name={`link-${index}`}
                                            type="url"
                                            value={link.url}
                                            inputMode="url"
                                            autoComplete="url"
                                            placeholder="https://"
                                            aria-label={`Link ${index + 1}`}
                                            onChange={(event) =>
                                                onLinkChange(link.id, event.target.value)
                                            }
                                        />
                                        {canRemoveLink ? (
                                            <button
                                                type="button"
                                                className={styles.removeLink}
                                                aria-label={`Quitar link ${index + 1}`}
                                                onClick={() => removeLink(link.id)}
                                            >
                                                ×
                                            </button>
                                        ) : null}
                                    </li>
                                );
                            })}
                        </ul>
                        {canAddLink ? (
                            <Button
                                type="button"
                                variant="secondary"
                                className={styles.addLink}
                                onClick={addLink}
                            >
                                Añadir link
                            </Button>
                        ) : null}
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
                        (step === 0 && !name)
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
