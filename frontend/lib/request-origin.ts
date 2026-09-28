import { headers } from "next/headers";

export async function requestOrigin() {
    const headerStore = await headers();
    const origin = headerStore.get("origin");
    if (origin) {
        return origin;
    }

    const host = headerStore.get("x-forwarded-host") ?? headerStore.get("host");
    const proto = headerStore.get("x-forwarded-proto") ?? "http";
    if (host) {
        return `${proto}://${host}`;
    }

    return "http://127.0.0.1:3000";
}
