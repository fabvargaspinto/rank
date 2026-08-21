import styles from './button.module.css';

type ButtonVariant = "primary" | "secondary";
type ButtonSize = "full" | "md";

export default function Button({
    children,
    onClick,
    variant = "primary",
    size = "md",
}: {
    children: React.ReactNode,
    onClick?: () => void,
    variant?: ButtonVariant,
    size?: ButtonSize,
}) {
    return (
        <button
            type="button"
            className={styles.button}
            onClick={onClick}
            data-variant={variant}
            data-size={size}
        >
            {children}
        </button>
    );
}
