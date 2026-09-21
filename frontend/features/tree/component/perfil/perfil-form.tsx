"use client";

import { useEffect, useId, useRef, useState, type ChangeEvent, type FormEvent } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import { updateUserAction } from "@/features/start/action/update-user-action";
import styles from "./perfil-form.module.css";

const NAME_MAX_LENGTH = 50;
const DESCRIPTION_MAX_LENGTH = 250;

export type Profile = {
    name: string;
    description: string;
    photo: string;
};

export function isObjectUrl(value: string): boolean {
    return value.startsWith("blob:") || value.startsWith("data:");
}

type PerfilFormProps = {
    profile: Profile;
    onSave: (next: Profile) => void;
};

export default function PerfilForm({ profile, onSave }: PerfilFormProps) {
    const nameId = useId();
    const descriptionId = useId();
    const [name, setName] = useState(profile.name);
    const [description, setDescription] = useState(profile.description);
    const [photo, setPhoto] = useState(profile.photo);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
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

    function onPhotoChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];

        if (!file || !file.type.startsWith("image/")) {
            return;
        }

        const url = URL.createObjectURL(file);

        setPhoto((current) => {
            if (isObjectUrl(current) && current !== profile.photo) {
                URL.revokeObjectURL(current);
            }

            return url;
        });
    }

    async function onSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const nextName = name.trim() || profile.name;

        if (!nextName) {
            setError("El nombre es obligatorio");
            return;
        }

        setSaving(true);
        setError("");

        const result = await updateUserAction({
            name: nextName,
            avatar: isObjectUrl(photo) ? profile.photo : photo,
            description: description.trim(),
        });

        setSaving(false);

        if (result.isError || !result.data) {
            setError(result.message || "No se pudo guardar tu perfil");
            return;
        }

        if (isObjectUrl(photo) && photo !== profile.photo) {
            URL.revokeObjectURL(photo);
        }

        onSave({
            name: result.data.name?.trim() || nextName,
            description: result.data.description ?? "",
            photo: result.data.avatar ?? "",
        });
    }

    return (
        <form className={styles.form} onSubmit={onSubmit}>
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
                        accept="image/*"
                        aria-labelledby={`${nameId}-photo`}
                        onChange={onPhotoChange}
                    />
                    <span className={styles.photoHint}>Cambiar foto</span>
                </label>
            </div>
            <div className={styles.field}>
                <label className={styles.fieldLabel} htmlFor={nameId}>
                    Nombre
                </label>
                <Input
                    id={nameId}
                    name="name"
                    value={name}
                    maxLength={NAME_MAX_LENGTH}
                    autoComplete="name"
                    placeholder="Nombre"
                    onChange={(event) => setName(event.target.value)}
                />
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
            {error ? (
                <p className={styles.error} role="alert">
                    {error}
                </p>
            ) : null}
            <Button type="submit" disabled={saving}>
                {saving ? "Guardando..." : "Guardar"}
            </Button>
        </form>
    );
}
