"use client";

import Drawer from "@/components/ui/drawer/drawer";
import PerfilForm, { isObjectUrl, type Profile } from "./perfil-form";
import styles from "./drawer-perfil.module.css";

export { isObjectUrl };
export type { Profile };

type DrawerPerfilProps = {
    profile: Profile;
    onSave: (next: Profile) => void;
};

function PencilIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="14"
            height="14"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" />
        </svg>
    );
}

export default function DrawerPerfil({ profile, onSave }: DrawerPerfilProps) {
    return (
        <Drawer
            title="Editar perfil"
            prompt={
                <button
                    type="button"
                    className={styles.prompt}
                    aria-label="Editar perfil"
                >
                    <PencilIcon />
                </button>
            }
        >
            {({ close }) => (
                <PerfilForm
                    profile={profile}
                    onSave={(next) => {
                        onSave(next);
                        close();
                    }}
                />
            )}
        </Drawer>
    );
}
