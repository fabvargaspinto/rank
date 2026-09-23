"use client";

import { useEffect, useRef, type RefObject } from "react";
import Avatar from "@/components/ui/avatar/avatar";
import styles from "./comments.module.css";

export type Comment = {
    id: string;
    avatar: string;
    user: string;
    date: string;
    text: string;
    link?: string;
};

type CommentsProps = {
    comments: Comment[];
    scrollRootRef: RefObject<HTMLElement | null>;
    hasMore: boolean;
    loadingMore: boolean;
    onLoadMore: () => void;
};

function formatCommentDate(value: string): string {
    const date = value.includes("T")
        ? new Date(value)
        : new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(date);
}

function hostnameFromUrl(url: string): string {
    try {
        return new URL(url).hostname.replace(/^www\./, "");
    } catch {
        return url;
    }
}

export default function Comments({
    comments,
    scrollRootRef,
    hasMore,
    loadingMore,
    onLoadMore,
}: CommentsProps) {
    const sentinelRef = useRef<HTMLLIElement>(null);

    useEffect(() => {
        const root = scrollRootRef.current;
        const sentinel = sentinelRef.current;

        if (!root || !sentinel || !hasMore) {
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0]?.isIntersecting) {
                    onLoadMore();
                }
            },
            {
                root,
                rootMargin: "120px 0px",
            },
        );

        observer.observe(sentinel);
        return () => observer.disconnect();
    }, [hasMore, onLoadMore, scrollRootRef, comments.length]);

    if (comments.length === 0 && !loadingMore) {
        return (
            <p className={styles.empty} role="status">
                No hay comentarios
            </p>
        );
    }

    return (
        <ul className={styles.feed} aria-label="Comentarios">
            {comments.map((comment) => (
                <li key={comment.id}>
                    <CommentItem {...comment} />
                </li>
            ))}
            {hasMore ? (
                <li ref={sentinelRef} className={styles.sentinel} aria-hidden={!loadingMore}>
                    {loadingMore ? (
                        <p className={styles.loading}>Cargando más...</p>
                    ) : null}
                </li>
            ) : null}
        </ul>
    );
}

function CommentItem({ avatar, user, date, text, link }: Omit<Comment, "id">) {
    return (
        <article className={styles.comment}>
            <Avatar src={avatar || null} name={user} size="sm" />
            <div className={styles.body}>
                <div className={styles.meta}>
                    <p className={styles.user}>{user}</p>
                    <time className={styles.date} dateTime={date}>
                        {formatCommentDate(date)}
                    </time>
                </div>
                <p className={styles.text}>{text}</p>
                {link ? (
                    <a
                        href={link}
                        className={styles.link}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {hostnameFromUrl(link)}
                    </a>
                ) : null}
            </div>
        </article>
    );
}
