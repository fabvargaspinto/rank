'use client';

import { useMemo } from 'react';

const DEFAULT_WIDTH = 100;
const DEFAULT_HEIGHT = 40;
const DEFAULT_PADDING = 3;

const MONTHS_SHORT = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

export type LinealChartPoint = {
    date: Date | string,
    followers: number,
};

export function useLinealChart({
    points,
    width = DEFAULT_WIDTH,
    height = DEFAULT_HEIGHT,
    padding = DEFAULT_PADDING,
}: {
    points: LinealChartPoint[],
    width?: number,
    height?: number,
    padding?: number,
}) {
    return useMemo(() => {
        const viewBox = `0 0 ${width} ${height}`;
        const innerWidth = width - padding * 2;
        const innerHeight = height - padding * 2;
        const baseline = height - padding;

        if (points.length === 0) {
            const y = padding + innerHeight / 2;
            const line = `M${padding} ${y} L${width - padding} ${y}`;

            return {
                line,
                area: '',
                viewBox,
                xTicks: [] as { labelMd: string, labelSm: string }[],
                dots: [] as { xPercent: number, yPercent: number, followers: number, label: string }[],
            };
        }

        const values = points.map((point) => point.followers);
        const min = Math.min(...values);
        const max = Math.max(...values);
        const range = max - min;
        const lastIndex = Math.max(points.length - 1, 1);

        const toY = (value: number) => range === 0
            ? padding + innerHeight / 2
            : padding + innerHeight - ((value - min) / range) * innerHeight;

        const plotted = points.map((point, index) => {
            const x = padding + (index / lastIndex) * innerWidth;
            const y = toY(point.followers);

            return {
                x,
                y,
                xPercent: (x / width) * 100,
                yPercent: (y / height) * 100,
                followers: point.followers,
                label: formatFollowers(point.followers),
                date: toDate(point.date),
            };
        });

        const line = plotted
            .map((point, index) => `${index === 0 ? 'M' : 'L'}${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
            .join(' ');

        const area = `${line} L${plotted[plotted.length - 1].x.toFixed(2)} ${baseline} L${plotted[0].x.toFixed(2)} ${baseline} Z`;

        const xTicks = plotted.map((point) => ({
            labelMd: formatDateMd(point.date),
            labelSm: formatDateSm(point.date),
        }));

        const dots = plotted.map((point) => ({
            xPercent: point.xPercent,
            yPercent: point.yPercent,
            followers: point.followers,
            label: point.label,
        }));

        return { line, area, viewBox, xTicks, dots };
    }, [points, width, height, padding]);
}

function toDate(value: Date | string) {
    return value instanceof Date ? value : new Date(value);
}

function formatDateMd(date: Date) {
    return `${date.getDate()} ${MONTHS_SHORT[date.getMonth()]}`;
}

function formatDateSm(date: Date) {
    return `${date.getDate()}/${date.getMonth() + 1}`;
}

function formatFollowers(value: number) {
    return Math.round(value).toLocaleString('es-ES');
}
