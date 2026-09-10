import FormHero from "@/pages/ui/form-hero/form-hero";
import Input from "@/pages/ui/input/input";

export default function LoginForm() {
    return (
        <FormHero
            description="Comunidad para musicos, astistas y creadores de contenido"
            submitLabel="Login"
            footerPrompt="no tienes una cuenta?"
            footerHref="/register"
            footerLabel="Registrate"
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" />
        </FormHero>
    );
}
