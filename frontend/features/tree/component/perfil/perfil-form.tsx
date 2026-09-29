"use client";

import { useId, useState, type ChangeEvent, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import DeleteAccountButton from "@/features/account/component/delete-account-button";
import AvatarPicker from "@/features/profile/avatar-picker";
import {
    firstLinkValidationError,
    linksForEditor,
    linksPayload,
    profileFromUserResponse,
    sanitizeName,
    sanitizeUsername,
    type Profile,
    type ProfileLink,
} from "@/features/profile/model";
import ProfileLinksEditor from "@/features/profile/profile-links-editor";
import { useAvatarUpload } from "@/features/profile/use-avatar-upload";
import { updateUserAction } from "@/features/start/action/update-user-action";
import { uploadAvatarAction } from "@/features/start/action/upload-avatar-action";
import { isUsernameFieldError } from "@/lib/api/types";
import {
    DESCRIPTION_MAX_LENGTH,
    DISPLAY_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    usernameShapeError,
} from "@/lib/domain-limits";
import styles from "./perfil-form.module.css";

const PROFILE_HOST = "sellonomada.com/";

export type { Profile, ProfileLink } from "@/features/profile/model";
export { isObjectUrl } from "@/features/profile/model";

type PerfilFormProps = {
    profile: Profile;
    onSave: (next: Profile) => void;
};

export default function PerfilForm({ profile, onSave }: PerfilFormProps) {
    const nameId = useId();
    const displayNameId = useId();
    const descriptionId = useId();
    const linksId = useId();
    const photoFieldId = useId();
    const [name, setName] = useState(profile.name);
    const [displayName, setDisplayName] = useState(profile.displayName);
    const [description, setDescription] = useState(profile.description);
    const [links, setLinks] = useState<ProfileLink[]>(() =>
        linksForEditor(profile.links),
    );
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [nameError, setNameError] = useState("");
    const [displayNameError, setDisplayNameError] = useState("");
    const {
        previewUrl: photo,
        file: photoFile,
        onFileChange,
        afterSave: afterAvatarSave,
    } = useAvatarUpload({
        initialUrl: profile.photo,
        preservedUrl: profile.photo,
    });

    async function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const validationError = await onFileChange(event);

        if (validationError) {
            setError(validationError);
            return;
        }

        setError("");
    }

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const nextName = sanitizeUsername(name) || sanitizeUsername(profile.name);
        const shapeError = usernameShapeError(nextName);

        if (shapeError) {
            setNameError(shapeError);
            return;
        }

        const linkError = firstLinkValidationError(links);

        if (linkError) {
            setError(linkError);
            return;
        }

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
                displayName: sanitizeName(displayName),
                description: sanitizeName(description),
                links: linksPayload(links),
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

            const nextPhoto = result.data.avatar ?? "";

            afterAvatarSave(nextPhoto);

            onSave(
                profileFromUserResponse(result.data, {
                    usernameFallback: nextName,
                }),
            );
        } catch {
            setError("No se pudo guardar tu perfil");
        } finally {
            setSaving(false);
        }
    }

    const trimmedName = sanitizeUsername(name);
    const savedUsername = trimmedName.toLowerCase();
    const lowercaseHint =
        trimmedName && trimmedName !== savedUsername
            ? `Se guarda en minúsculas: ${savedUsername}`
            : "";
    const usernameChanged =
        savedUsername !== sanitizeUsername(profile.name).toLowerCase();
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
                    <span className={styles.fieldLabel} id={photoFieldId}>
                        Foto
                    </span>
                    <AvatarPicker
                        variant="banner"
                        previewUrl={photo}
                        fallbackName={
                            sanitizeName(displayName) ||
                            trimmedName ||
                            profile.name
                        }
                        ariaLabelledBy={photoFieldId}
                        onChange={onPhotoChange}
                    />
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
                        maxLength={USERNAME_MAX_LENGTH}
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
