"use client";

import { useEffect, useId, useRef, useState } from "react";
import styles from "./hcaptcha-field.module.css";

type HcaptchaApi = {
    render: (
        element: HTMLElement,
        options: {
            sitekey: string;
            callback: (token: string) => void;
            "expired-callback": () => void;
            "error-callback": () => void;
        },
    ) => string;
    reset: (widgetId: string) => void;
    remove: (widgetId: string) => void;
};

declare global {
    interface Window {
        hcaptcha?: HcaptchaApi;
    }
}

const SCRIPT_ID = "hcaptcha-script";
const SCRIPT_SRC = "https://js.hcaptcha.com/1/api.js?render=explicit";

function loadHcaptchaScript(): Promise<HcaptchaApi> {
    if (window.hcaptcha) {
        return Promise.resolve(window.hcaptcha);
    }

    const existing = document.getElementById(SCRIPT_ID);
    if (existing) {
        return new Promise((resolve, reject) => {
            existing.addEventListener("load", () => {
                if (window.hcaptcha) {
                    resolve(window.hcaptcha);
                } else {
                    reject(new Error("hCaptcha no cargó"));
                }
            });
            existing.addEventListener("error", () =>
                reject(new Error("hCaptcha no cargó")),
            );
        });
    }

    return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.id = SCRIPT_ID;
        script.src = SCRIPT_SRC;
        script.async = true;
        script.onload = () => {
            if (window.hcaptcha) {
                resolve(window.hcaptcha);
            } else {
                reject(new Error("hCaptcha no cargó"));
            }
        };
        script.onerror = () => reject(new Error("hCaptcha no cargó"));
        document.head.appendChild(script);
    });
}

type HcaptchaFieldProps = {
    siteKey: string;
    /** Remontar / resetear el widget (p. ej. después de un error). */
    resetSignal?: string | number | boolean;
};

export default function HcaptchaField({
    siteKey,
    resetSignal,
}: HcaptchaFieldProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const widgetIdRef = useRef<string | null>(null);
    const [token, setToken] = useState("");
    const reactId = useId();

    useEffect(() => {
        let cancelled = false;
        const container = containerRef.current;
        if (!container) {
            return;
        }

        setToken("");
        void loadHcaptchaScript()
            .then((hcaptcha) => {
                if (cancelled || !containerRef.current) {
                    return;
                }
                if (widgetIdRef.current) {
                    hcaptcha.remove(widgetIdRef.current);
                    widgetIdRef.current = null;
                }
                container.innerHTML = "";
                widgetIdRef.current = hcaptcha.render(container, {
                    sitekey: siteKey,
                    callback: (value) => setToken(value),
                    "expired-callback": () => setToken(""),
                    "error-callback": () => setToken(""),
                });
            })
            .catch(() => {
                if (!cancelled) {
                    setToken("");
                }
            });

        return () => {
            cancelled = true;
            if (widgetIdRef.current && window.hcaptcha) {
                window.hcaptcha.remove(widgetIdRef.current);
                widgetIdRef.current = null;
            }
        };
    }, [siteKey, resetSignal, reactId]);

    return (
        <div className={styles.wrap}>
            <input type="hidden" name="captchaToken" value={token} />
            <div ref={containerRef} />
        </div>
    );
}

export function hcaptchaSiteKeyFromEnv(): string | null {
    const key = process.env.NEXT_PUBLIC_HCAPTCHA_SITE_KEY?.trim();
    return key || null;
}
