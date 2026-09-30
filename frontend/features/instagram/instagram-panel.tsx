"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import Chart from "@/components/ui/chart/chart";
import Button from "@/components/ui/button/button";
import type {
    FollowerHistoryItemResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";
import {
    connectInstagramAction,
    disconnectInstagramAction,
} from "./actions";
import {
    formatFollowerDelta,
    formatFollowers,
    historyToChart,
    weekLabel,
    type InstagramOAuthStatus,
} from "./model";
import styles from "./instagram-panel.module.css";

export default function InstagramPanel({
    initialConnection,
    initialHistory,
    oauthStatus,
}: {
    initialConnection: InstagramConnectionResponse;
    initialHistory: FollowerHistoryItemResponse[];
    oauthStatus?: InstagramOAuthStatus;
}) {
    const router = useRouter();
    const [connection, setConnection] = useState(initialConnection);
    const [history, setHistory] = useState(initialHistory);
    const [showHistory, setShowHistory] = useState(initialHistory.length > 1);
    const [message, setMessage] = useState(() => oauthMessage(oauthStatus));
    const [pending, startTransition] = useTransition();

    useEffect(() => {
        if (!oauthStatus) {
            return;
        }
        router.replace("/dashboard/tree", { scroll: false });
    }, [oauthStatus, router]);

    function connect() {
        startTransition(async () => {
            const result = await connectInstagramAction();
            if (result.isError) {
                setMessage(result.message || "No se pudo conectar Instagram");
            }
        });
    }

    function disconnect() {
        startTransition(async () => {
            const result = await disconnectInstagramAction();
            if (result.isError) {
                setMessage(result.message || "No se pudo desconectar Instagram");
                return;
            }
            setConnection({
                connected: false,
                username: null,
                instagram_account_id: null,
                followers_count: null,
                followers_delta: null,
            });
            setHistory([]);
            setShowHistory(false);
            setMessage(null);
        });
    }

    const followers = connection.followers_count;
    const delta = connection.followers_delta;

    return (
        <section className={styles.panel} aria-label="Instagram">
            <header className={styles.header}>
                <div>
                    <p className={styles.network}>Instagram</p>
                    <p className={styles.status}>
                        {connection.connected && connection.username
                            ? `@${connection.username}`
                            : "No conectado"}
                    </p>
                </div>
                {connection.connected && followers !== null ? (
                    <div className={styles.summary}>
                        <p className={styles.metricLabel}>Followers</p>
                        <p className={styles.metricValue}>
                            {formatFollowers(followers)}
                        </p>
                        {delta !== null ? (
                            <p
                                className={
                                    delta >= 0 ? styles.deltaUp : styles.deltaDown
                                }
                            >
                                {formatFollowerDelta(delta)} esta semana
                            </p>
                        ) : null}
                    </div>
                ) : null}
            </header>
            {message ? <p className={styles.message}>{message}</p> : null}
            <div className={styles.actions}>
                {connection.connected ? (
                    <>
                        <Button
                            type="button"
                            variant="secondary"
                            disabled={pending || history.length === 0}
                            onClick={() => setShowHistory((open) => !open)}
                        >
                            {showHistory ? "Ocultar evolución" : "Ver evolución"}
                        </Button>
                        <Button
                            type="button"
                            variant="danger"
                            disabled={pending}
                            onClick={disconnect}
                        >
                            Desconectar
                        </Button>
                    </>
                ) : (
                    <Button type="button" disabled={pending} onClick={connect}>
                        Conectar Instagram
                    </Button>
                )}
            </div>
            {connection.connected && showHistory ? (
                <FollowerEvolution items={history} />
            ) : null}
        </section>
    );
}

function FollowerEvolution({ items }: { items: FollowerHistoryItemResponse[] }) {
    if (items.length === 0) {
        return (
            <p className={styles.empty}>Todavía no hay capturas semanales.</p>
        );
    }

    return (
        <div className={styles.history}>
            <h2 className={styles.historyTitle}>Evolución de followers</h2>
            <Chart
                data={historyToChart(items)}
                formatValue={formatFollowers}
                aria-label="Evolución semanal de followers de Instagram"
            />
            <table className={styles.table}>
                <caption className={styles.srOnly}>
                    Historial semanal de followers
                </caption>
                <thead>
                    <tr>
                        <th scope="col">Semana</th>
                        <th scope="col">Followers</th>
                        <th scope="col">Variación</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map((item) => (
                        <tr key={item.week_start}>
                            <td>{weekLabel(item.week_start)}</td>
                            <td>{formatFollowers(item.followers_count)}</td>
                            <td>
                                {item.delta === null
                                    ? "—"
                                    : formatFollowerDelta(item.delta)}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function oauthMessage(status: InstagramOAuthStatus): string | null {
    if (status === "connected") {
        return "Instagram quedó conectado.";
    }
    if (status === "error") {
        return "No se pudo conectar Instagram. Volvé a intentarlo.";
    }
    return null;
}
