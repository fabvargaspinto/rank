import { Children, cloneElement, isValidElement } from 'react';
import styles from './button.module.css';

type ButtonVariant = "primary" | "secondary";
type ButtonSize = "full" | "md";

export default function Button({
    children,
    onClick,
    variant = "primary",
    size = "md",
    asChild = false,
    disabled = false,
}: {
    children: React.ReactNode,
    onClick?: () => void,
    variant?: ButtonVariant,
    size?: ButtonSize,
    asChild?: boolean,
    disabled?: boolean,
}) {
    const className = styles.button;

    if (asChild) {
        const child = Children.only(children);

        if (!isValidElement<{ className?: string; 'data-variant'?: ButtonVariant; 'data-size'?: ButtonSize }>(child)) {
            return child;
        }

        return cloneElement(child, {
            className: [className, child.props.className].filter(Boolean).join(' '),
            'data-variant': variant,
            'data-size': size,
        });
    }

    return (
        <button
            type="button"
            className={className}
            onClick={onClick}
            disabled={disabled}
            data-variant={variant}
            data-size={size}
        >
            {children}
        </button>
    );
}
