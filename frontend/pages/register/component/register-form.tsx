import FormHero from "@/pages/ui/form-hero/form-hero";
import Input from "@/pages/ui/input/input";

export default function RegisterForm() {
    return (
        <FormHero
           
            description="Crea tu cuenta para participar de la comunidad nómada"
            submitLabel="Register"
            footerPrompt="ya tienes una cuenta?"
            footerHref="/"
            footerLabel="Inicia sesión"
        >
            <Input type="email" name="email" placeholder="Email" autoComplete="email" />
            <Input type="password" name="password" placeholder="Password" />
            <Input type="password" name="passwordConfirmation" placeholder="Password Confirmation" />
        </FormHero>
    );
}
