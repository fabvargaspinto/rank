import styles from './input.module.css';

type InputSize = "full" | "md";
type InputType = "text" | "email" | "password";

export default function Input({
    label,
    type = "text",
    placeholder,
    name,
    id,
    value,
    onChange,
    disabled,
    size = "md",
}: {
    label?: string,
    type?: InputType,
    placeholder?: string,
    name?: string,
    id?: string,
    value?: string,
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void,
    disabled?: boolean,
    size?: InputSize,
}) {
    const inputId = id ?? name;

    const field = (
        <input
            id={inputId}
            name={name}
            type={type}
            placeholder={placeholder}
            value={value}
            onChange={onChange}
            disabled={disabled}
            className={styles.input}
            data-size={size}
        />
    );

    if (!label) {
        return field;
    }

    return (
        <div className={styles.field}>
            <label htmlFor={inputId} className={styles.label}>
                {label}
            </label>
            {field}
        </div>
    );
}
