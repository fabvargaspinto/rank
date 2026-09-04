import styles from './text-area.module.css';

type TextAreaSize = "full" | "md";

export default function Textarea({
    label,
    placeholder,
    name,
    id,
    value,
    onChange,
    disabled,
    size = "md",
    rows = 4,
}: {
    label?: string,
    placeholder?: string,
    name?: string,
    id?: string,
    value?: string,
    onChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void,
    disabled?: boolean,
    size?: TextAreaSize,
    rows?: number,
}) {
    const textareaId = id ?? name;

    const field = (
        <textarea
            id={textareaId}
            name={name}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            disabled={disabled}
            rows={rows}
            className={styles.textarea}
            data-size={size}
        />
    );

    if (!label) {
        return field;
    }

    return (
        <div className={styles.field}>
            <label htmlFor={textareaId} className={styles.label}>
                {label}
            </label>
            {field}
        </div>
    );
}
