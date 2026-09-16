"use client";

import {
    cloneElement,
    isValidElement,
    useEffect,
    useId,
    useRef,
    useState,
    type MouseEvent,
    type ReactElement,
    type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import styles from "./drawer.module.css";

type DrawerSide = "bottom" | "left" | "right";
type DrawerMotion = "open" | "closed";

const DRAWER_MOTION_MS = 240;

type DrawerHelpers = {
    close: () => void;
};

type PromptElement = ReactElement<{
    onClick?: (event: MouseEvent<HTMLElement>) => void;
    type?: string;
    "aria-expanded"?: boolean | "true" | "false";
    "aria-haspopup"?: "dialog" | boolean | "false" | "true" | "menu" | "listbox" | "tree" | "grid";
    "aria-controls"?: string;
}>;

type DrawerProps = {
    prompt?: PromptElement;
    open?: boolean;
    onOpen?: () => void;
    onClose?: () => void;
    children?: ReactNode | ((helpers: DrawerHelpers) => ReactNode);
    side?: DrawerSide;
    title?: string;
    label?: string;
    className?: string;
};

export default function Drawer({
    prompt,
    open: openProp,
    onOpen,
    onClose,
    children,
    side = "right",
    title,
    label,
    className,
}: DrawerProps) {
    const titleId = useId();
    const panelId = useId();
    const panelRef = useRef<HTMLDivElement>(null);
    const previouslyFocused = useRef<HTMLElement | null>(null);
    const onOpenRef = useRef(onOpen);
    const onCloseRef = useRef(onClose);
    const closeRef = useRef<() => void>(() => {});
    const [mounted, setMounted] = useState(false);
    const [rendered, setRendered] = useState(false);
    const [motion, setMotion] = useState<DrawerMotion>("closed");
    const [uncontrolledOpen, setUncontrolledOpen] = useState(false);
    const controlled = openProp !== undefined;
    const open = controlled ? openProp : uncontrolledOpen;
    const content = typeof children === "function" ? children({ close }) : children;

    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;

    function openDrawer() {
        if (!controlled) {
            setUncontrolledOpen(true);
        }

        onOpenRef.current?.();
    }

    function close() {
        if (!controlled) {
            setUncontrolledOpen(false);
        }

        onCloseRef.current?.();
    }

    closeRef.current = close;

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

        body.style.overflow = "hidden";
        if (scrollbarWidth > 0) {
            body.style.paddingRight = `${scrollbarWidth}px`;
        }

        return () => {
            body.style.overflow = previousBodyOverflow;
            body.style.paddingRight = previousBodyPaddingRight;
        };
    }, [rendered]);

    useEffect(() => {
        if (!open || !rendered) {
            return;
        }

        previouslyFocused.current =
            document.activeElement instanceof HTMLElement
                ? document.activeElement
                : null;

        panelRef.current?.focus({ preventScroll: true });

        function onKeyDown(event: KeyboardEvent) {
            if (event.key === "Escape") {
                closeRef.current();
            }
        }

        document.addEventListener("keydown", onKeyDown);

        return () => {
            document.removeEventListener("keydown", onKeyDown);
        };
    }, [open, rendered]);

    useEffect(() => {
        if (rendered) {
            return;
        }

        previouslyFocused.current?.focus({ preventScroll: true });
    }, [rendered]);

    const promptNode =
        prompt && isValidElement(prompt)
            ? cloneElement(prompt, {
                  "aria-haspopup": "dialog",
                  "aria-expanded": open,
                  "aria-controls": rendered ? panelId : undefined,
                  onClick: (event: MouseEvent<HTMLElement>) => {
                      prompt.props.onClick?.(event);

                      if (!event.defaultPrevented) {
                          openDrawer();
                      }
                  },
              })
            : prompt;

    const overlay =
        mounted && rendered
            ? createPortal(
                  <div className={styles.drawer} data-side={side} data-state={motion}>
                      <button
                          type="button"
                          className={styles.backdrop}
                          onClick={close}
                          aria-label="Cerrar"
                      />
                      <div
                          ref={panelRef}
                          id={panelId}
                          className={[styles.panel, className].filter(Boolean).join(" ")}
                          role="dialog"
                          aria-modal="true"
                          aria-labelledby={title ? titleId : undefined}
                          aria-label={!title ? label ?? "Panel" : undefined}
                          tabIndex={-1}
                      >
                          {side === "bottom" ? (
                              <div className={styles.handle} aria-hidden="true" />
                          ) : null}
                          <header className={styles.header}>
                              {title ? (
                                  <h2 id={titleId} className={styles.title}>
                                      {title}
                                  </h2>
                              ) : null}
                              <button
                                  type="button"
                                  className={styles.close}
                                  onClick={close}
                                  aria-label="Cerrar"
                              >
                                  <svg
                                      width="16"
                                      height="16"
                                      viewBox="0 0 16 16"
                                      fill="none"
                                      aria-hidden="true"
                                  >
                                      <path
                                          d="M4 4l8 8M12 4l-8 8"
                                          stroke="currentColor"
                                          strokeWidth="1.5"
                                          strokeLinecap="round"
                                      />
                                  </svg>
                              </button>
                          </header>
                          {content ? <div className={styles.content}>{content}</div> : null}
                      </div>
                  </div>,
                  document.body,
              )
            : null;

    if (!promptNode) {
        return overlay;
    }

    return (
        <>
            {promptNode}
            {overlay}
        </>
    );
}
