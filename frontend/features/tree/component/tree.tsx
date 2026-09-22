"use client";

import { useId, useState } from "react";
import Image from "next/image";
import type { CommentResponse, UserResponse } from "@/lib/fetch_data";
import Comments, { INITIAL_COMMENTS, type Comment } from "./comment/comments";
import DrawerComment from "./comment/drawer-comment";
import DrawerPerfil, { isObjectUrl, type Profile } from "./perfil/drawer-perfil";
import SocialLinkIcon, {
    socialLinkLabel,
    socialLinkTypeFromUrl,
    socialLinkTypeFromValue,
} from "./social-link-icon";
import Socials from "./socials/socials";
import styles from "./tree.module.css";

type TabId = "comments" | "socials";

const TABS: { id: TabId; label: string }[] = [
    { id: "comments", label: "Comentarios" },
    { id: "socials", label: "Redes" },
];

function profileFromUser(user: UserResponse): Profile {
    return {
        name: user.name?.trim() || "Sin nombre",
        description: user.description ?? "",
        photo: user.avatar ?? "",
        links: (user.links ?? []).map((link) => ({
            id: link.id,
            url: link.url,
            type: link.type,
        })),
    };
}

function hasPhoto(photo: string): boolean {
    return photo.trim().length > 0;
}

function isExternalPhoto(photo: string): boolean {
    return isObjectUrl(photo) || /^https?:\/\//.test(photo);
}

export default function Tree({
    user,
    editable = false,
}: {
    user: UserResponse;
    editable?: boolean;
}) {
    const tabsId = useId();
    const [tab, setTab] = useState<TabId>("comments");
    const [profile, setProfile] = useState<Profile>(() => profileFromUser(user));
    const [feed, setFeed] = useState<Comment[]>(INITIAL_COMMENTS);

    function addComment(created: CommentResponse) {
        setFeed((current) => [
            {
                id: created.id,
                avatar: profile.photo,
                user: profile.name,
                date: created.created_at,
                text: created.text,
                ...(created.link ? { link: created.link } : {}),
            },
            ...current,
        ]);
    }

    return (
        <article className={styles.container}>
            <TreeHeader
                profile={profile}
                editable={editable}
                onSaveProfile={setProfile}
            />
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
                {tab === "comments" && editable ? (
                    <DrawerComment onAdd={addComment} />
                ) : null}
            </div>
        </article>
    );
}

function ChevronIcon({ up = false }: { up?: boolean }) {
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
            {up ? <path d="M6 15l6-6 6 6" /> : <path d="M6 9l6 6 6-6" />}
        </svg>
    );
}

function TreeHeader({
    profile,
    editable,
    onSaveProfile,
}: {
    profile: Profile;
    editable: boolean;
    onSaveProfile: (next: Profile) => void;
}) {
    const [linksExpanded, setLinksExpanded] = useState(false);
    const links = profile.links
        .filter((link) => link.url.trim().length > 0)
        .slice(0, 6)
        .map((link) => {
            const type = link.type
                ? socialLinkTypeFromValue(link.type)
                : socialLinkTypeFromUrl(link.url);

            return {
                id: link.id,
                type,
                label: socialLinkLabel(type),
                url: link.url,
            };
        });
    const canExpandLinks = links.length > 3;

    return (
        <header className={styles.header}>
            {hasPhoto(profile.photo) ? (
                isExternalPhoto(profile.photo) ? (
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
                )
            ) : null}
            {editable ? (
                <DrawerPerfil profile={profile} onSave={onSaveProfile} />
            ) : null}
            <div className={styles.headerContent}>
                {links.length > 0 ? (
                    <div className={styles.headerLinksWrap}>
                        {canExpandLinks ? (
                            <button
                                type="button"
                                className={styles.headerLinksToggle}
                                aria-expanded={linksExpanded}
                                aria-label={
                                    linksExpanded
                                        ? "Mostrar menos redes"
                                        : "Mostrar más redes"
                                }
                                onClick={() => setLinksExpanded((open) => !open)}
                            >
                                <ChevronIcon up={!linksExpanded} />
                            </button>
                        ) : null}
                        <div
                            className={[
                                styles.headerLinksContainer,
                                canExpandLinks
                                    ? linksExpanded
                                        ? styles.headerLinksExpanded
                                        : styles.headerLinksCollapsed
                                    : "",
                            ]
                                .filter(Boolean)
                                .join(" ")}
                        >
                            {links.map(({ id, type, label, url }) => (
                                <a
                                    key={id}
                                    href={url}
                                    className={styles.headerLink}
                                    aria-label={label}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <SocialLinkIcon type={type} />
                                </a>
                            ))}
                        </div>
                    </div>
                ) : null}
                <h1 className={styles.headerTitle}>{profile.name}</h1>
                {profile.description ? (
                    <p className={styles.headerDescription}>{profile.description}</p>
                ) : null}
            </div>
        </header>
    );
}
