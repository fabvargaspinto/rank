"use client";

import { useId, useState } from "react";
import Image from "next/image";
import Comments, { INITIAL_COMMENTS, type Comment } from "./comment/comments";
import DrawerComment, { type CommentDraft } from "./comment/drawer-comment";
import DrawerPerfil, { isObjectUrl, type Profile } from "./perfil/drawer-perfil";
import Socials from "./socials/socials";
import styles from "./tree.module.css";

type TabId = "comments" | "socials";

const DEFAULT_PROFILE: Profile = {
    name: "Luna Reyes",
    description: "Cantautora. Canciones nuevas cada semana.",
    photo: "/demo.jpg",
};

const TABS: { id: TabId; label: string }[] = [
    { id: "comments", label: "Comentarios" },
    { id: "socials", label: "Redes" },
];

export default function Tree() {
    const tabsId = useId();
    const [tab, setTab] = useState<TabId>("socials");
    const [profile, setProfile] = useState<Profile>(DEFAULT_PROFILE);
    const [feed, setFeed] = useState<Comment[]>(INITIAL_COMMENTS);

    function saveProfile(next: Profile) {
        setProfile((current) => {
            if (isObjectUrl(current.photo) && current.photo !== next.photo) {
                URL.revokeObjectURL(current.photo);
            }

            return next;
        });
    }

    function addComment(draft: CommentDraft) {
        const today = new Date().toISOString().slice(0, 10);

        setFeed((current) => [
            {
                id: current.reduce((max, comment) => Math.max(max, comment.id), 0) + 1,
                avatar: "",
                user: "",
                date: today,
                text: draft.text,
                link: draft.link,
            },
            ...current,
        ]);
    }

    return (
        <article className={styles.container}>
            <TreeHeader profile={profile} onSaveProfile={saveProfile} />
            <div
                className={styles.tabs}
                role="tablist"
                aria-label="Secciones del perfil"
            >
                {TABS.map(({ id, label }) => {
                    const selected = tab === id;

                    return (
                        <button
                            key={id}
                            type="button"
                            role="tab"
                            id={`${tabsId}-${id}`}
                            aria-selected={selected}
                            aria-controls={`${tabsId}-${id}-panel`}
                            className={[styles.tab, selected ? styles.tabActive : ""]
                                .filter(Boolean)
                                .join(" ")}
                            onClick={() => setTab(id)}
                        >
                            {label}
                        </button>
                    );
                })}
            </div>
            <div className={styles.panelWrap}>
                <div
                    className={styles.panel}
                    role="tabpanel"
                    id={`${tabsId}-${tab}-panel`}
                    aria-labelledby={`${tabsId}-${tab}`}
                >
                    {tab === "comments" ? <Comments comments={feed} /> : <Socials />}
                </div>
                {tab === "comments" ? <DrawerComment onAdd={addComment} /> : null}
            </div>
        </article>
    );
}

function TreeHeader({
    profile,
    onSaveProfile,
}: {
    profile: Profile;
    onSaveProfile: (next: Profile) => void;
}) {
    return (
        <header className={styles.header}>
            {isObjectUrl(profile.photo) ? (
                <img
                    src={profile.photo}
                    alt=""
                    className={styles.headerImage}
                />
            ) : (
                <Image
                    src={profile.photo}
                    alt=""
                    fill
                    priority
                    sizes="(max-width: 480px) 100vw, 450px"
                    className={styles.headerImage}
                />
            )}
            <DrawerPerfil profile={profile} onSave={onSaveProfile} />
            <div className={styles.headerContent}>
                <h1 className={styles.headerTitle}>{profile.name}</h1>
                {profile.description ? (
                    <p className={styles.headerDescription}>{profile.description}</p>
                ) : null}
            </div>
        </header>
    );
}
