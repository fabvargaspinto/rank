import type { ComponentProps } from "react";
import Button from "../button/button";
import GoogleIcon from "./google-icon";

type GoogleButtonProps = Omit<ComponentProps<typeof Button>, "variant" | "children"> & {
    children?: ComponentProps<typeof Button>["children"];
};

export default function GoogleButton({
    type = "button",
    children = "Continue with Google",
    ...props
}: GoogleButtonProps) {
    return (
        <Button type={type} variant="secondary" {...props}>
            <GoogleIcon />
            {children}
        </Button>
    );
}
