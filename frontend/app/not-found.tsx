import Link from "next/link";
import Button from "@/components/ui/button/button";
import StatusScreen from "@/components/ui/status-screen/status-screen";

export default function NotFound() {
    return (
        <StatusScreen
            title="Esta página no existe"
            description="El perfil que buscás no está."
            action={
                <Link href="/">
                    <Button>Volver al inicio</Button>
                </Link>
            }
        />
    );
}
