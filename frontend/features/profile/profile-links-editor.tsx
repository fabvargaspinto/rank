"use client";

import { useId } from "react";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import { MAX_LINKS } from "@/lib/domain-limits";
import { createEmptyLink, type ProfileLink } from "@/features/profile/model";
import styles from "./profile-links-editor.module.css";

type ProfileLinksEditorProps = {
    links: ProfileLink[];
    onLinksChange: (links: ProfileLink[]) => void;
    id?: string;
};

export default function ProfileLinksEditor({
    links,
    onLinksChange,
    id,
}: ProfileLinksEditorProps) {
    const generatedId = useId();
    const linksId = id ?? generatedId;
    const canAddLink = links.length < MAX_LINKS;
    const canRemoveLink = links.length > 1;

    function onLinkChange(linkId: string, url: string) {
        onLinksChange(
            links.map((link) =>
                link.id === linkId ? { ...link, url } : link,
            ),
        );
    }

    function addLink() {
        if (links.length >= MAX_LINKS) {
            return;
        }

        onLinksChange([...links, createEmptyLink()]);
    }

    function removeLink(linkId: string) {
        if (links.length <= 1) {
            return;
        }

        onLinksChange(links.filter((link) => link.id !== linkId));
    }

    return (
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
    );
}
