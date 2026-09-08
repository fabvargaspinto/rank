import type { ComponentProps } from "react";
import styles from "./input.module.css";

type InputProps = ComponentProps<"input">;

export default function Input({ className, ...props }: InputProps) {
    return (
        <input
            className={[styles.input, className].filter(Boolean).join(" ")}
            {...props}
        />
    );
}
