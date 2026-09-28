const LOCAL_SITE_URL = "http://localhost:3000";

export function siteUrl() {
    const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");

    if (configured) {
        return configured;
    }

    return LOCAL_SITE_URL;
}
