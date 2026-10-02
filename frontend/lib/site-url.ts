const LOCAL_SITE_URL = "http://localhost:3000";

export function siteUrl() {
    const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim().replace(/\/$/, "");

    if (configured) {
        return configured;
    }

    if (process.env.NODE_ENV === "production") {
        throw new Error("Falta NEXT_PUBLIC_SITE_URL");
    }

    return LOCAL_SITE_URL;
}

export function profileHost() {
    return `${new URL(siteUrl()).host}/`;
}
