import type { ComponentProps } from "react";
import styles from "./button.module.css";

type ButtonProps = ComponentProps<"button">;

export default function Button({ className, type = "button", ...props }: ButtonProps) {
    return (
        <button
            type={type}
            className={[styles.button, className].filter(Boolean).join(" ")}
            {...props}
        />
    );
}
