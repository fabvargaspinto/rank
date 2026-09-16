"use client";

import { useId, useState, type PointerEvent } from "react";
import styles from "./chart.module.css";

export type ChartPoint = {
    label: string;
    compactLabel?: string;
    value: number;
};

type ChartProps = {
    data: ChartPoint[];
    formatValue?: (value: number) => string;
    className?: string;
    "aria-label"?: string;
};

const VIEW_WIDTH = 360;
const VIEW_HEIGHT = 140;
const PAD = { top: 16, right: 8, bottom: 8, left: 8 };
const LABEL_COUNT = 4;

function defaultFormatValue(value: number): string {
    return new Intl.NumberFormat("es-ES", { useGrouping: true }).format(value);
}

function coordinates(data: ChartPoint[]) {
    const values = data.map((point) => point.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;
    const paddedMin = min - range * 0.12;
    const paddedMax = max + range * 0.12;
    const innerWidth = VIEW_WIDTH - PAD.left - PAD.right;
    const innerHeight = VIEW_HEIGHT - PAD.top - PAD.bottom;

    return data.map((point, index) => {
        const x =
            data.length === 1
                ? PAD.left + innerWidth / 2
                : PAD.left + (index / (data.length - 1)) * innerWidth;
        const t = (point.value - paddedMin) / (paddedMax - paddedMin);
        const y = PAD.top + innerHeight * (1 - t);

        return { x, y, ...point };
    });
}

function linePath(points: { x: number; y: number }[]): string {
    return points
        .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
        .join(" ");
}

function labelIndexes(total: number): number[] {
    if (total <= 0) {
        return [];
    }

    if (total <= LABEL_COUNT) {
        return Array.from({ length: total }, (_, index) => index);
    }

    return Array.from({ length: LABEL_COUNT }, (_, index) =>
        Math.round((index * (total - 1)) / (LABEL_COUNT - 1)),
    );
}

function areaPath(points: { x: number; y: number }[]): string {
    if (points.length === 0) {
        return "";
    }

    const baseline = VIEW_HEIGHT - PAD.bottom;
    const first = points[0];
    const last = points[points.length - 1];

    return `${linePath(points)} L ${last.x} ${baseline} L ${first.x} ${baseline} Z`;
}

export default function Chart({
    data,
    formatValue = defaultFormatValue,
    className,
    "aria-label": ariaLabel,
}: ChartProps) {
    const rawId = useId().replace(/:/g, "");
    const gradientId = `chart-area-${rawId}`;
    const [activeIndex, setActiveIndex] = useState<number | null>(null);
    const points = data.length > 0 ? coordinates(data) : [];
    const active = activeIndex !== null ? points[activeIndex] : null;
    const visibleLabels = labelIndexes(points.length);

    function handlePointerMove(event: PointerEvent<SVGSVGElement>) {
        if (points.length === 0) {
            return;
        }

        const rect = event.currentTarget.getBoundingClientRect();
        const viewX = ((event.clientX - rect.left) / rect.width) * VIEW_WIDTH;
        let nearest = 0;
        let nearestDistance = Infinity;

        points.forEach((point, index) => {
            const distance = Math.abs(point.x - viewX);
            if (distance < nearestDistance) {
                nearest = index;
                nearestDistance = distance;
            }
        });

        setActiveIndex(nearest);
    }

    if (data.length === 0) {
        return <p className={styles.empty}>No hay datos para mostrar.</p>;
    }

    return (
        <div className={[styles.chart, className].filter(Boolean).join(" ")}>
            <table className={styles.srOnly}>
                {ariaLabel ? <caption>{ariaLabel}</caption> : null}
                <thead>
                    <tr>
                        <th>Semana</th>
                        <th>Valor</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((point) => (
                        <tr key={point.label}>
                            <td>{point.label}</td>
                            <td>{formatValue(point.value)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div
                className={[styles.tooltip, active ? styles.tooltipVisible : ""]
                    .filter(Boolean)
                    .join(" ")}
                aria-hidden="true"
            >
                {active ? (
                    <>
                        <span className={styles.labelFull}>{active.label}</span>
                        <span className={styles.labelCompact}>
                            {active.compactLabel ?? active.label}
                        </span>
                        {` · ${formatValue(active.value)}`}
                    </>
                ) : (
                    ""
                )}
            </div>
            <svg
                className={styles.svg}
                viewBox={`0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}`}
                preserveAspectRatio="none"
                role="presentation"
                onPointerMove={handlePointerMove}
                onPointerLeave={() => setActiveIndex(null)}
            >
                <defs>
                    <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                        <stop
                            offset="0%"
                            stopColor="var(--chart-area-color)"
                            stopOpacity="0.28"
                        />
                        <stop
                            offset="100%"
                            stopColor="var(--chart-area-color)"
                            stopOpacity="0"
                        />
                    </linearGradient>
                </defs>
                <line
                    className={styles.axis}
                    x1={PAD.left}
                    x2={VIEW_WIDTH - PAD.right}
                    y1={VIEW_HEIGHT - PAD.bottom}
                    y2={VIEW_HEIGHT - PAD.bottom}
                />
                <path d={areaPath(points)} style={{ fill: `url(#${gradientId})` }} />
                <path className={styles.line} d={linePath(points)} />
                {active ? (
                    <>
                        <line
                            className={styles.guide}
                            x1={active.x}
                            x2={active.x}
                            y1={PAD.top}
                            y2={VIEW_HEIGHT - PAD.bottom}
                        />
                        <circle className={styles.point} cx={active.x} cy={active.y} r="4" />
                    </>
                ) : null}
            </svg>
            <div className={styles.labels} aria-hidden="true">
                {visibleLabels.map((index) => {
                    const point = points[index];

                    return (
                        <span key={point.label} className={styles.label}>
                            <span className={styles.labelFull}>{point.label}</span>
                            <span className={styles.labelCompact}>
                                {point.compactLabel ?? point.label}
                            </span>
                        </span>
                    );
                })}
            </div>
        </div>
    );
}
