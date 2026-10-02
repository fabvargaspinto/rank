"use client";

import { useRouter } from "next/navigation";
import Button from "@/components/ui/button/button";
import StatusScreen from "@/components/ui/status-screen/status-screen";

export default function UnavailablePage() {
    const router = useRouter();

    return (
        <StatusScreen
            title="No se pudo cargar"
            description="Probá de nuevo en unos segundos."
            action={
                <Button onClick={() => router.refresh()}>Reintentar</Button>
            }
        />
    );
}
