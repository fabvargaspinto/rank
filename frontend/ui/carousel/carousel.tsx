'use client';

import { Children, useLayoutEffect, useRef, useState } from 'react';
import styles from './carousel.module.css';

export default function Carousel({
    children,
    index,
    label,
}: {
    children: React.ReactNode,
    index: number,
    label?: string,
}) {
    const slides = Children.toArray(children);
    const slideCount = slides.length;
    const clampedIndex = slideCount === 0
        ? 0
        : Math.min(Math.max(index, 0), slideCount - 1);

    const slideRefs = useRef<Array<HTMLDivElement | null>>([]);
    const previousIndex = useRef(clampedIndex);
    const [height, setHeight] = useState<number>();

    useLayoutEffect(() => {
        const slide = slideRefs.current[clampedIndex];
        if (!slide) {
            return;
        }

        const updateHeight = () => {
            setHeight(slide.offsetHeight);
        };

        updateHeight();
        const observer = new ResizeObserver(updateHeight);
        observer.observe(slide);

        return () => observer.disconnect();
    }, [clampedIndex, slideCount]);

    useLayoutEffect(() => {
        if (previousIndex.current === clampedIndex) {
            return;
        }

        previousIndex.current = clampedIndex;

        const active = document.activeElement;
        if (active instanceof HTMLElement) {
            active.blur();
        }
    }, [clampedIndex]);

    return (
        <div
            className={styles.carousel}
            style={height !== undefined ? { height: `${height}px` } : undefined}
            role="region"
            aria-roledescription="carousel"
            aria-label={label}
        >
            <div
                className={styles.track}
                style={{ transform: `translateX(-${clampedIndex * 100}%)` }}
            >
                {slides.map((slide, slideIndex) => {
                    const isActive = slideIndex === clampedIndex;

                    return (
                        <div
                            key={slideIndex}
                            ref={(node) => {
                                slideRefs.current[slideIndex] = node;
                            }}
                            className={styles.slide}
                            aria-hidden={!isActive}
                            inert={!isActive}
                        >
                            {slide}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
