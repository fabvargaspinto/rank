import { Children, cloneElement, isValidElement } from 'react';
import styles from './button.module.css';

type ButtonVariant = "primary" | "secondary" | "tertiary";
type ButtonSize = "full" | "md" | "sm" | "icon-md"; 

export default function Button({
    children,
    className: classNameProps,
    onClick,
    variant = "primary",
    size = "md",
    asChild = false,
    disabled = false,
    type = "button",
}: {
    children: React.ReactNode,
    onClick?: () => void,
    variant?: ButtonVariant,
    size?: ButtonSize,
    asChild?: boolean,
    disabled?: boolean,
    type?: "button" | "submit",
    className?: string,
}) {
    const className = [styles.button, classNameProps].filter(Boolean).join(' ');

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
            type={type}
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
