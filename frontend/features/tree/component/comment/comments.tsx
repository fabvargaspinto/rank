"use client";

import { useEffect, useId, useRef, useState, type RefObject } from "react";
import { createPortal } from "react-dom";
import Avatar from "@/components/ui/avatar/avatar";
import Button from "@/components/ui/button/button";
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
    onDelete?: (id: string) => Promise<{ isError: boolean; message: string }>;
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
    onDelete,
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
                    <CommentItem
                        {...comment}
                        onDelete={
                            onDelete ? () => onDelete(comment.id) : undefined
                        }
                    />
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

function CommentItem({
    avatar,
    user,
    date,
    text,
    link,
    onDelete,
}: Omit<Comment, "id"> & {
    onDelete?: () => Promise<{ isError: boolean; message: string }>;
}) {
    const titleId = useId();
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [open, setOpen] = useState(false);
    const [pending, setPending] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const dialog = dialogRef.current;

        if (!dialog) {
            return;
        }

        if (open && !dialog.open) {
            dialog.showModal();
        }

        if (!open && dialog.open) {
            dialog.close();
        }
    }, [open]);

    function close() {
        if (pending) {
            return;
        }

        setOpen(false);
        setError("");
    }

    async function confirm() {
        if (!onDelete) {
            return;
        }

        setPending(true);
        setError("");

        try {
            const result = await onDelete();

            if (result.isError) {
                setError(result.message || "No se pudo borrar el comentario");
                return;
            }

            setOpen(false);
        } catch {
            setError("No se pudo borrar el comentario");
        } finally {
            setPending(false);
        }
    }

    return (
        <article className={styles.comment}>
            <Avatar src={avatar || null} name={user} size="sm" />
            <div className={styles.body}>
                <div className={styles.meta}>
                    <p className={styles.user}>{user}</p>
                    <time className={styles.date} dateTime={date}>
                        {formatCommentDate(date)}
                    </time>
                    {onDelete ? (
                        <button
                            type="button"
                            className={styles.remove}
                            aria-label="Borrar comentario"
                            onClick={() => {
                                setError("");
                                setOpen(true);
                            }}
                        >
                            ×
                        </button>
                    ) : null}
                </div>
                {open
                    ? createPortal(
                          <dialog
                              ref={dialogRef}
                              className={styles.dialog}
                              aria-labelledby={titleId}
                              onClose={close}
                              onClick={(event) => {
                                  if (event.target === event.currentTarget) {
                                      close();
                                  }
                              }}
                          >
                              <div className={styles.dialogBody}>
                                  <h2 id={titleId} className={styles.dialogTitle}>
                                      Borrar comentario
                                  </h2>
                                  <p className={styles.dialogCopy}>
                                      Se borra este comentario. Esta acción no se
                                      puede deshacer.
                                  </p>
                                  {error ? (
                                      <p className={styles.dialogError} role="alert">
                                          {error}
                                      </p>
                                  ) : null}
                                  <div className={styles.dialogActions}>
                                      <Button
                                          type="button"
                                          variant="secondary"
                                          onClick={close}
                                          disabled={pending}
                                      >
                                          Cancelar
                                      </Button>
                                      <Button
                                          type="button"
                                          variant="danger"
                                          onClick={() => {
                                              void confirm();
                                          }}
                                          disabled={pending}
                                      >
                                          {pending ? "Borrando..." : "Borrar"}
                                      </Button>
                                  </div>
                              </div>
                          </dialog>,
                          document.body,
                      )
                    : null}
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
