"use client";

import { useEffect, useId, useRef, useState, type ChangeEvent, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import DeleteAccountButton from "@/features/account/component/delete-account-button";
import { updateUserAction } from "@/features/start/action/update-user-action";
import { uploadAvatarAction } from "@/features/start/action/upload-avatar-action";
import { isUsernameFieldError } from "@/lib/fetch_data";
import { prepareAvatar } from "@/lib/prepare-avatar";
import styles from "./perfil-form.module.css";

const DESCRIPTION_MAX_LENGTH = 250;
const PROFILE_HOST = "sellonomada.com/";
const MAX_LINKS = 6;
const MAX_AVATAR_BYTES = 2 * 1024 * 1024;
const AVATAR_MIME_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

export type ProfileLink = {
    id: string;
    url: string;
    type?: string;
};

export type Profile = {
    name: string;
    displayName: string;
    description: string;
    photo: string;
    links: ProfileLink[];
};

export function isObjectUrl(value: string): boolean {
    return value.startsWith("blob:") || value.startsWith("data:");
}

export function createEmptyLink(id = crypto.randomUUID()): ProfileLink {
    return { id, url: "" };
}

function linksForForm(links: ProfileLink[]): ProfileLink[] {
    if (links.length === 0) {
        return [createEmptyLink("link-0")];
    }

    return links.slice(0, MAX_LINKS).map((link, index) => ({
        id: link.id || `link-${index}`,
        url: link.url,
        type: link.type,
    }));
}

type PerfilFormProps = {
    profile: Profile;
    onSave: (next: Profile) => void;
};

export default function PerfilForm({ profile, onSave }: PerfilFormProps) {
    const nameId = useId();
    const displayNameId = useId();
    const descriptionId = useId();
    const linksId = useId();
    const [name, setName] = useState(profile.name);
    const [displayName, setDisplayName] = useState(profile.displayName);
    const [description, setDescription] = useState(profile.description);
    const [photo, setPhoto] = useState(profile.photo);
    const [photoFile, setPhotoFile] = useState<File | null>(null);
    const [links, setLinks] = useState<ProfileLink[]>(() => linksForForm(profile.links));
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [nameError, setNameError] = useState("");
    const [displayNameError, setDisplayNameError] = useState("");
    const photoRef = useRef(photo);
    const savedPhotoRef = useRef(profile.photo);

    photoRef.current = photo;
    savedPhotoRef.current = profile.photo;

    useEffect(() => {
        return () => {
            const draftPhoto = photoRef.current;

            if (isObjectUrl(draftPhoto) && draftPhoto !== savedPhotoRef.current) {
                URL.revokeObjectURL(draftPhoto);
            }
        };
    }, []);

    async function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];
        event.target.value = "";

        if (!file) {
            return;
        }

        if (!AVATAR_MIME_TYPES.has(file.type)) {
            setError("La imagen debe ser JPEG, PNG o WebP");
            return;
        }

        const prepared = await prepareAvatar(file);

        if (prepared.size > MAX_AVATAR_BYTES) {
            setError("La imagen no puede superar 2 MB");
            return;
        }

        setError("");
        const url = URL.createObjectURL(prepared);
        setPhotoFile(prepared);

        setPhoto((current) => {
            if (isObjectUrl(current) && current !== profile.photo) {
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

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const nextName = name.trim() || profile.name;

        if (!nextName) {
            setNameError("El usuario es obligatorio");
            return;
        }

        const nextLinks = links
            .map((link) => ({ id: link.id, url: link.url.trim() }))
            .filter((link) => link.url.length > 0)
            .slice(0, MAX_LINKS);

        setSaving(true);
        setError("");
        setNameError("");

        try {
            if (photoFile) {
                const uploaded = await uploadAvatarAction(photoFile);

                if (uploaded.isError || !uploaded.data) {
                    setError(uploaded.message || "No se pudo subir la imagen");
                    return;
                }
            }

            const result = await updateUserAction({
                name: nextName,
                displayName,
                description: description.trim(),
                links: nextLinks.map((link) => ({ url: link.url })),
            });

            if (result.isError || !result.data) {
                if (isUsernameFieldError(result)) {
                    setNameError(result.message || "Ese usuario no es válido");
                    return;
                }

                if (result.field === "display_name") {
                    setDisplayNameError(result.message || "Ese nombre no es válido");
                    return;
                }

                setError(result.message || "No se pudo guardar tu perfil");
                return;
            }

            if (isObjectUrl(photo) && photo !== profile.photo) {
                URL.revokeObjectURL(photo);
            }

            setPhotoFile(null);

            onSave({
                name: result.data.name?.trim() || nextName,
                displayName: result.data.display_name?.trim() || "",
                description: result.data.description ?? "",
                photo: result.data.avatar ?? "",
                links: (result.data.links ?? []).map((link) => ({
                    id: link.id,
                    url: link.url,
                    type: link.type,
                })),
            });
        } catch {
            setError("No se pudo guardar tu perfil");
        } finally {
            setSaving(false);
        }
    }

    const canAddLink = links.length < MAX_LINKS;
    const canRemoveLink = links.length > 1;
    const trimmedName = name.trim();
    const savedUsername = trimmedName.toLowerCase();
    const lowercaseHint =
        trimmedName && trimmedName !== savedUsername
            ? `Se guarda en minúsculas: ${savedUsername}`
            : "";
    const usernameChanged = savedUsername !== profile.name.trim().toLowerCase();
    const nameDescribedBy = [
        `${nameId}-url`,
        lowercaseHint ? `${nameId}-hint` : "",
        usernameChanged ? `${nameId}-warning` : "",
        nameError ? `${nameId}-error` : "",
    ]
        .filter(Boolean)
        .join(" ");

    return (
        <form className={styles.form} onSubmit={onSubmit}>
            <div className={styles.body}>
                <div className={styles.field}>
                    <span className={styles.fieldLabel} id={`${nameId}-photo`}>
                        Foto
                    </span>
                    <label className={styles.photoPicker}>
                        {photo ? (
                            <img src={photo} alt="" className={styles.photoPreview} />
                        ) : null}
                        <input
                            className={styles.photoInput}
                            type="file"
                            accept="image/jpeg,image/png,image/webp"
                            aria-labelledby={`${nameId}-photo`}
                            onChange={onPhotoChange}
                        />
                        <span className={styles.photoHint}>Cambiar foto</span>
                    </label>
                </div>
                <div className={styles.field}>
                    <label className={styles.fieldLabel} htmlFor={nameId}>
                        Usuario
                    </label>
                    <Input
                        id={nameId}
                        name="name"
                        value={name}
                        autoComplete="username"
                        spellCheck={false}
                        placeholder="usuario"
                        aria-invalid={Boolean(nameError)}
                        aria-describedby={nameDescribedBy}
                        onChange={(event) => {
                            setName(event.target.value);
                            setNameError("");
                        }}
                    />
                    {lowercaseHint ? (
                        <p id={`${nameId}-hint`} className={styles.hint}>
                            {lowercaseHint}
                        </p>
                    ) : null}
                    <p id={`${nameId}-url`} className={styles.hint}>
                        Tu URL pública es {PROFILE_HOST}
                        {profile.name}
                    </p>
                    {usernameChanged ? (
                        <p id={`${nameId}-warning`} className={styles.hint}>
                            Si lo cambiás, esa URL deja de funcionar y los
                            enlaces que ya compartiste también.
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
                        placeholder="Luna Reyes"
                        maxLength={50}
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
                <div className={styles.deleteSection}>
                    <DeleteAccountButton username={profile.name} />
                </div>
            </div>
            <div className={styles.footer}>
                {error ? (
                    <p className={styles.error} role="alert">
                        {error}
                    </p>
                ) : null}
                <Button type="submit" disabled={saving}>
                    {saving ? "Guardando..." : "Guardar"}
                </Button>
            </div>
        </form>
    );
}
