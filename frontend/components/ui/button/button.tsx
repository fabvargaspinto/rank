import type { ComponentProps } from "react";
import styles from "./button.module.css";

type ButtonVariant = "primary" | "secondary";

type ButtonProps = ComponentProps<"button"> & {
    variant?: ButtonVariant;
};

export default function Button({
    className,
    type = "button",
    variant = "primary",
    ...props
}: ButtonProps) {
    return (
        <button
            type={type}
            className={[styles.button, styles[variant], className].filter(Boolean).join(" ")}
            {...props}
        />
    );
}
