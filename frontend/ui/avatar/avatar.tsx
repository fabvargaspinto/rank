import styles from './avatar.module.css';

type AvatarSize = "sm" | "md" | "lg";

export default function Avatar({
    src,
    alt,
    size = "md",
    fallback,
}: {
    src?: string,
    alt: string,
    size?: AvatarSize,
    fallback?: string,
}) {
    const initials = getInitials(fallback ?? alt);

    return (
        <span className={styles.avatar} data-size={size}>
            {src ? (
                <img src={src} alt={alt} />
            ) : (
                <span className={styles.fallback} role="img" aria-label={alt}>
                    {initials}
                </span>
            )}
        </span>
    );
}

function getInitials(value: string) {
    const parts = value.trim().split(/\s+/).filter(Boolean);

    if (parts.length === 0) {
        return "?";
    }

    if (parts.length === 1) {
        return parts[0].charAt(0).toUpperCase();
    }

    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
}
