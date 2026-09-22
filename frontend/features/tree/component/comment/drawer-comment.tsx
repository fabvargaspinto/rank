"use client";

import Drawer from "@/components/ui/drawer/drawer";
import type { CommentResponse } from "@/lib/fetch_data";
import CommentForm from "./comment-form";
import styles from "./drawer-comment.module.css";

type DrawerCommentProps = {
    onAdd: (comment: CommentResponse) => void;
};

function PlusIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            aria-hidden="true"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
        >
            <path d="M12 5v14M5 12h14" />
        </svg>
    );
}

export default function DrawerComment({ onAdd }: DrawerCommentProps) {
    return (
        <Drawer
            title="Añadir comentario"
            prompt={
                <button
                    type="button"
                    className={styles.prompt}
                    aria-label="Añadir comentario"
                >
                    <PlusIcon />
                </button>
            }
        >
            {({ close }) => (
                <CommentForm
                    onAdd={(comment) => {
                        onAdd(comment);
                        close();
                    }}
                />
            )}
        </Drawer>
    );
}
