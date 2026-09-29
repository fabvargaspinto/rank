"use client";

import Drawer from "@/components/ui/drawer/drawer";
import type { PostResponse } from "@/lib/fetch_data";
import PostForm from "./post-form";
import styles from "./drawer-post.module.css";

type DrawerPostProps = {
    onAdd: (post: PostResponse) => void;
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

export default function DrawerPost({ onAdd }: DrawerPostProps) {
    return (
        <Drawer
            title="Nueva publicación"
            prompt={
                <button
                    type="button"
                    className={styles.prompt}
                    aria-label="Nueva publicación"
                >
                    <PlusIcon />
                </button>
            }
        >
            {({ close }) => (
                <PostForm
                    onAdd={(post) => {
                        onAdd(post);
                        close();
                    }}
                />
            )}
        </Drawer>
    );
}
