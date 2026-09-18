"use client";

import { Children, type ReactNode } from "react";
import styles from "./carousel.module.css";

type CarouselProps = {
    index: number;
    children: ReactNode;
    className?: string;
    label?: string;
};

export default function Carousel({
    index,
    children,
    className,
    label,
}: CarouselProps) {
    const slides = Children.toArray(children);
    const lastIndex = Math.max(slides.length - 1, 0);
    const safeIndex = Math.min(Math.max(index, 0), lastIndex);

    return (
        <div
            className={[styles.root, className].filter(Boolean).join(" ")}
            aria-roledescription="carrusel"
            aria-label={label}
        >
            <div className={styles.track}>
                {slides.map((slide, slideIndex) => {
                    const active = slideIndex === safeIndex;

                    return (
                        <div
                            key={slideIndex}
                            className={[
                                styles.slide,
                                active ? styles.slideActive : "",
                            ]
                                .filter(Boolean)
                                .join(" ")}
                            aria-hidden={!active}
                            inert={!active}
                        >
                            {slide}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
