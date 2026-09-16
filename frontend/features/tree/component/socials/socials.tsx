"use client";

import Chart, { type ChartPoint } from "@/components/ui/chart/chart";
import styles from "./socials.module.css";

type Social = {
    id: string;
    label: string;
    href: string;
};

const socials: Social[] = [
    { id: "instagram", label: "Instagram", href: "https://instagram.com" },
    { id: "youtube", label: "YouTube", href: "https://youtube.com" },
    { id: "spotify", label: "Spotify", href: "https://spotify.com" },
];

function chartPoint(isoDate: string, value: number): ChartPoint {
    const date = new Date(`${isoDate}T00:00:00`);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");

    return {
        label: new Intl.DateTimeFormat("es", {
            day: "numeric",
            month: "short",
        })
            .format(date)
            .replace(".", ""),
        compactLabel: `${day}-${month}`,
        value,
    };
}

const weeklyFollowers: ChartPoint[] = [
    chartPoint("2026-07-28", 1240),
    chartPoint("2026-08-04", 1310),
    chartPoint("2026-08-11", 1295),
    chartPoint("2026-08-18", 1420),
    chartPoint("2026-08-25", 1505),
    chartPoint("2026-09-01", 1480),
    chartPoint("2026-09-08", 1610),
    chartPoint("2026-09-15", 1750),
];

function formatFollowers(value: number): string {
    return new Intl.NumberFormat("es-ES", { useGrouping: true }).format(value);
}

function formatFollowerDelta(value: number): string {
    const formatted = formatFollowers(Math.abs(value));

    if (value > 0) {
        return `+${formatted}`;
    }

    if (value < 0) {
        return `−${formatted}`;
    }

    return formatted;
}

export default function Socials() {
    return (
        <div className={styles.socials}>
            <SocialOptions />
            <SocialChart />
        </div>
    );
}

function SocialOptions() {
    return (
        <ul className={styles.options} aria-label="Redes">
            {socials.map((social) => (
                <li key={social.id} className={styles.item} />
            ))}
        </ul>
    );
}

function SocialChart() {
    const current = weeklyFollowers.at(-1)?.value ?? 0;
    const previous = weeklyFollowers.at(-2)?.value ?? current;
    const delta = current - previous;

    return (
        <section className={styles.chart} aria-label="Seguidores por semana">
            <div className={styles.chartHeader}>
                <div className={styles.chartSummary}>
                    <p className={styles.chartTitle}>Seguidores</p>
                    <p className={styles.chartValue}>{formatFollowers(current)}</p>
                </div>
                <p className={delta >= 0 ? styles.deltaUp : styles.deltaDown}>
                    {formatFollowerDelta(delta)} esta semana
                </p>
            </div>
            <Chart
                data={weeklyFollowers}
                formatValue={formatFollowers}
                aria-label={`Seguidores por semana: de ${formatFollowers(weeklyFollowers[0]?.value ?? 0)} a ${formatFollowers(current)} en ${weeklyFollowers.length} semanas`}
            />
        </section>
    );
}
