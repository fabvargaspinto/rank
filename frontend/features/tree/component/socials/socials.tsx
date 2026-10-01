"use client";

import { useEffect, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import Avatar from "@/components/ui/avatar/avatar";
import Button from "@/components/ui/button/button";
import Chart from "@/components/ui/chart/chart";
import Drawer from "@/components/ui/drawer/drawer";
import SocialLinkIcon from "@/features/tree/component/social-link-icon";
import {
    connectInstagramAction,
    disconnectInstagramAction,
} from "@/features/instagram/actions";
import {
    formatFollowerDelta,
    formatFollowers,
    historyToChart,
    weekLabel,
    type InstagramOAuthStatus,
} from "@/features/instagram/model";
import type {
    FollowerHistoryItemResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";
import styles from "./socials.module.css";

export default function Socials({
    editable = false,
    oauthStatus,
    initialConnection,
    initialHistory = [],
}: {
    editable?: boolean;
    oauthStatus?: InstagramOAuthStatus;
    initialConnection?: InstagramConnectionResponse;
    initialHistory?: FollowerHistoryItemResponse[];
}) {
    const router = useRouter();
    const [connection, setConnection] = useState(
        () =>
            initialConnection ?? {
                connected: false,
                username: null,
                instagram_account_id: null,
                followers_count: null,
                followers_delta: null,
            },
    );
    const [history, setHistory] = useState(initialHistory);
    const [message, setMessage] = useState(() => oauthMessage(oauthStatus));
    const [pending, startTransition] = useTransition();
    const [drawerOpen, setDrawerOpen] = useState(false);

    useEffect(() => {
        if (!oauthStatus) {
            return;
        }
        router.replace("/dashboard/tree", { scroll: false });
    }, [oauthStatus, router]);

    if (!editable) {
        return (
            <p className={styles.emptyPublic}>
                Todavía no hay métricas para mostrar.
            </p>
        );
    }

    function connectInstagram() {
        startTransition(async () => {
            const result = await connectInstagramAction();
            if (result.isError) {
                setMessage(result.message || "No se pudo conectar Instagram");
                setDrawerOpen(false);
            }
        });
    }

    function disconnectInstagram() {
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
            setMessage(null);
        });
    }

    const connected = connection.connected;
    const chartPoints = historyToChart(history);
    const followers = connection.followers_count;
    const delta = connection.followers_delta;

    return (
        <div className={styles.socials}>
            {message ? <p className={styles.message}>{message}</p> : null}

            {connected ? (
                <ConnectedView
                    connection={connection}
                    history={history}
                    chartPoints={chartPoints}
                    followers={followers}
                    delta={delta}
                    pending={pending}
                    onOpenNetworks={() => setDrawerOpen(true)}
                />
            ) : (
                <EmptyView
                    pending={pending}
                    onSync={() => setDrawerOpen(true)}
                />
            )}

            <Drawer
                title="Redes"
                open={drawerOpen}
                onOpen={() => setDrawerOpen(true)}
                onClose={() => setDrawerOpen(false)}
            >
                {({ close }) => (
                    <div className={styles.drawerBody}>
                        <p className={styles.drawerHint}>
                            Elegí una red para sincronizar. Solo leemos datos
                            públicos de la cuenta que autorices.
                        </p>
                        <ul className={styles.networkList}>
                            <li>
                                <button
                                    type="button"
                                    className={styles.networkOption}
                                    disabled={pending || connected}
                                    onClick={() => {
                                        if (connected) {
                                            close();
                                            return;
                                        }
                                        connectInstagram();
                                    }}
                                >
                                    <span className={styles.networkOptionIcon}>
                                        <SocialLinkIcon type="instagram" />
                                    </span>
                                    <span className={styles.networkOptionText}>
                                        <span className={styles.networkOptionName}>
                                            Instagram
                                        </span>
                                        <span className={styles.networkOptionStatus}>
                                            {connected
                                                ? "Ya conectada"
                                                : "Sincronizar cuenta"}
                                        </span>
                                    </span>
                                </button>
                            </li>
                        </ul>
                        {connected ? (
                            <Button
                                type="button"
                                variant="danger"
                                disabled={pending}
                                onClick={() => {
                                    disconnectInstagram();
                                    close();
                                }}
                            >
                                Desconectar Instagram
                            </Button>
                        ) : null}
                    </div>
                )}
            </Drawer>
        </div>
    );
}

function EmptyView({
    pending,
    onSync,
}: {
    pending: boolean;
    onSync: () => void;
}) {
    return (
        <section className={styles.emptyState} aria-label="Redes">
            <p className={styles.emptyCopy}>
                Para poder sincronizar tus redes necesitamos permiso para leer
                tus datos públicos.
            </p>
            <Button
                type="button"
                className={styles.syncButton}
                disabled={pending}
                onClick={onSync}
            >
                Sincroniza tus redes
            </Button>
        </section>
    );
}

function ConnectedView({
    connection,
    history,
    chartPoints,
    followers,
    delta,
    pending,
    onOpenNetworks,
}: {
    connection: InstagramConnectionResponse;
    history: FollowerHistoryItemResponse[];
    chartPoints: ReturnType<typeof historyToChart>;
    followers: number | null;
    delta: number | null;
    pending: boolean;
    onOpenNetworks: () => void;
}) {
    const username = connection.username ?? "usuario";

    return (
        <section className={styles.connected} aria-label="Redes">
            <div className={styles.linkedBlock}>
                <p className={styles.linkedLabel}>Redes vinculadas</p>
                <div className={styles.linkedRow}>
                    <button
                        type="button"
                        className={[styles.networkChip, styles.networkChipActive]
                            .filter(Boolean)
                            .join(" ")}
                        aria-label="Instagram"
                        aria-current="true"
                    >
                        <SocialLinkIcon type="instagram" />
                    </button>
                    <button
                        type="button"
                        className={styles.networkChip}
                        aria-label="Agregar red"
                        disabled={pending}
                        onClick={onOpenNetworks}
                    >
                        <PlusIcon />
                    </button>
                </div>
            </div>

            <article className={styles.accountCard}>
                <Avatar name={username} size="md" />
                <div className={styles.accountMeta}>
                    <p className={styles.accountUser}>@{username}</p>
                    <p className={styles.accountNetwork}>Instagram</p>
                    {followers !== null ? (
                        <p className={styles.accountFollowers}>
                            {formatFollowers(followers)} followers
                            {delta !== null ? (
                                <span
                                    className={
                                        delta >= 0
                                            ? styles.deltaUp
                                            : styles.deltaDown
                                    }
                                >
                                    {" "}
                                    {formatFollowerDelta(delta)} esta semana
                                </span>
                            ) : null}
                        </p>
                    ) : null}
                </div>
                <button
                    type="button"
                    className={styles.accountMenu}
                    aria-label="Opciones de Instagram"
                    disabled={pending}
                    onClick={onOpenNetworks}
                >
                    <MoreIcon />
                </button>
            </article>

            <div className={styles.chartBlock}>
                {chartPoints.length > 0 ? (
                    <>
                        <Chart
                            data={chartPoints}
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
                                {history.map((item) => (
                                    <tr key={item.week_start}>
                                        <td>{weekLabel(item.week_start)}</td>
                                        <td>
                                            {formatFollowers(item.followers_count)}
                                        </td>
                                        <td>
                                            {item.delta === null
                                                ? "—"
                                                : formatFollowerDelta(item.delta)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </>
                ) : (
                    <p className={styles.chartEmpty}>
                        Todavía no hay capturas semanales para el gráfico.
                    </p>
                )}
            </div>
        </section>
    );
}

function PlusIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
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

function MoreIcon() {
    return (
        <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            aria-hidden="true"
            fill="currentColor"
        >
            <circle cx="12" cy="5" r="1.5" />
            <circle cx="12" cy="12" r="1.5" />
            <circle cx="12" cy="19" r="1.5" />
        </svg>
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
