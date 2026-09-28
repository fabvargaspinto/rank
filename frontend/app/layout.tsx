import type { Metadata } from "next";
import { siteUrl } from "@/lib/site-url";
import "./reset.css";
import "./primitives.css";
import "./semantic.css";
import "./globals.css";

export const metadata: Metadata = {
    metadataBase: new URL(siteUrl()),
    title: {
        default: "Sello Nómada",
        template: "%s · Sello Nómada",
    },
    description: "Comunidad de artistas, músicos y creadores digitales.",
    openGraph: {
        type: "website",
        locale: "es",
        siteName: "Sello Nómada",
    },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
    return (
        <html lang="es">
            <body>{children}</body>
        </html>
    );
}
