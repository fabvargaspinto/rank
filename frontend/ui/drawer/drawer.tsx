'use client';

import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import styles from "./drawer.module.css";

type DrawerSide = "bottom" | "left" | "right";
type DrawerMotion = "open" | "closed";

const DRAWER_MOTION_MS = 240;

export default function Drawer({
    open,
    onClose,
    children,
    side = "right",
    title,
    label,
}: {
    open: boolean,
    onClose: () => void,
    children?: ReactNode,
    side?: DrawerSide,
    title?: string,
    label?: string,
}) {
    const titleId = useId();
    const panelRef = useRef<HTMLDivElement>(null);
    const previouslyFocused = useRef<HTMLElement | null>(null);
    const [mounted, setMounted] = useState(false);
    const [rendered, setRendered] = useState(false);
    const [motion, setMotion] = useState<DrawerMotion>("closed");

    if (open && !rendered) {
        setRendered(true);
    }

    useEffect(() => {
        setMounted(true);
    }, []);

    useEffect(() => {
        if (!rendered) {
            return;
        }

        if (open) {
            const frame = requestAnimationFrame(() => setMotion("open"));
            return () => cancelAnimationFrame(frame);
        }

        setMotion("closed");
        const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const timeout = window.setTimeout(
            () => setRendered(false),
            reducedMotion ? 0 : DRAWER_MOTION_MS,
        );

        return () => clearTimeout(timeout);
    }, [open, rendered]);

    useEffect(() => {
        if (!rendered) {
            return;
        }

        const { body, documentElement } = document;
        const scrollbarWidth = window.innerWidth - documentElement.clientWidth;
        const previousBodyOverflow = body.style.overflow;
        const previousBodyPaddingRight = body.style.paddingRight;
        const previousHtmlOverflow = documentElement.style.overflow;

        body.style.overflow = "hidden";
        documentElement.style.overflow = "hidden";
        if (scrollbarWidth > 0) {
            body.style.paddingRight = `${scrollbarWidth}px`;
        }

        return () => {
            body.style.overflow = previousBodyOverflow;
            body.style.paddingRight = previousBodyPaddingRight;
            documentElement.style.overflow = previousHtmlOverflow;
        };
    }, [rendered]);

    useEffect(() => {
        if (!open || !rendered) {
            return;
        }

        previouslyFocused.current = document.activeElement instanceof HTMLElement
            ? document.activeElement
            : null;

        panelRef.current?.focus({ preventScroll: true });

        function onKeyDown(event: KeyboardEvent) {
            if (event.key === "Escape") {
                onClose();
            }
        }

        document.addEventListener("keydown", onKeyDown);

        return () => {
            document.removeEventListener("keydown", onKeyDown);
        };
    }, [open, rendered, onClose]);

    useEffect(() => {
        if (rendered) {
            return;
        }

        previouslyFocused.current?.focus({ preventScroll: true });
    }, [rendered]);

    if (!mounted || !rendered) {
        return null;
    }

    return createPortal(
        <div className={styles.drawer} data-side={side} data-state={motion}>
            <button
                type="button"
                className={styles.backdrop}
                onClick={onClose}
                aria-label="Cerrar"
            />
            <div
                ref={panelRef}
                className={styles.panel}
                role="dialog"
                aria-modal="true"
                aria-labelledby={title ? titleId : undefined}
                aria-label={!title ? label : undefined}
                tabIndex={-1}
            >
                {side === "bottom" ? <div className={styles.handle} aria-hidden="true" /> : null}
                <header className={styles.header}>
                    {title ? <h2 id={titleId} className={styles.title}>{title}</h2> : null}
                    <button
                        type="button"
                        className={styles.close}
                        onClick={onClose}
                        aria-label="Cerrar"
                    >
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
                            <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    </button>
                </header>
                {children ? (
                    <div className={styles.content}>
                        {children}
                    </div>
                ) : null}
            </div>
        </div>,
        document.body,
    );
}
