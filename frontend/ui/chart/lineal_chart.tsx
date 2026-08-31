'use client';

import { useState } from 'react';
import { useLinealChart, type LinealChartPoint } from './lineal_chart_hook';
import styles from './lineal_chart.module.css';

export default function LinealChart({
    points,
  
}: {
    points: LinealChartPoint[],

}) {
    const { line, area, viewBox, xTicks, dots } = useLinealChart({ points });
    const lastIndex = dots.length === 0 ? null : dots.length - 1;
    const [hovered, setHovered] = useState<number | null>(lastIndex);
    const hoveredDot = hovered === null ? null : dots[hovered];
    const activate = (index: number | null) => setHovered(index ?? lastIndex);

    return (
        <figure className={styles.chart}>
            <div className={styles.frame}>
                <div className={styles.plot}>
                    <svg
                        className={styles.svg}
                        viewBox={viewBox}
                        preserveAspectRatio="none"
                        aria-hidden="true"
                    >
                        {area ? <path className={styles.area} d={area} /> : null}
                        <path className={styles.line} d={line} />
                    </svg>
                    {dots.map((dot, index) => (
                        <button
                            key={`${dot.xPercent}-${dot.yPercent}`}
                            type="button"
                            className={styles.dot}
                            style={{ left: `${dot.xPercent}%`, top: `${dot.yPercent}%` }}
                            aria-label={`${dot.label} followers`}
                            aria-pressed={hovered === index}
                            onPointerEnter={() => activate(index)}
                            onPointerLeave={() => activate(lastIndex)}
                            onFocus={() => activate(index)}
                            onBlur={() => activate(lastIndex)}
                        />
                    ))}
                    {hoveredDot ? (
                        <div
                            className={styles.tooltip + (hoveredDot.yPercent < 18 ? ` ${styles.tooltipBelow}` : '')}
                            style={{ left: `${hoveredDot.xPercent}%`, top: `${hoveredDot.yPercent}%` }}
                            role="status"
                        >
                            {hoveredDot.label}
                        </div>
                    ) : null}
                </div>
                <div className={styles.xAxis} aria-hidden="true">
                    {xTicks.map((tick) => (
                        <span key={tick.labelSm} className={styles.xTick}>
                            <span className={styles.labelMd}>{tick.labelMd}</span>
                            <span className={styles.labelSm}>{tick.labelSm}</span>
                        </span>
                    ))}
                </div>
            </div>
        </figure>
    );
}
