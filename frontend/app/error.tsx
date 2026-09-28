"use client";

import Button from "@/components/ui/button/button";
import StatusScreen from "@/components/ui/status-screen/status-screen";

type ErrorPageProps = {
    reset: () => void;
};

export default function ErrorPage({ reset }: ErrorPageProps) {
    return (
        <StatusScreen
            title="No se pudo cargar"
            description="Probá de nuevo en unos segundos."
            action={<Button onClick={reset}>Reintentar</Button>}
        />
    );
}
