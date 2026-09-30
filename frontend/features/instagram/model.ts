import type {
    FollowerHistoryItemResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";

export function formatFollowers(value: number): string {
    return new Intl.NumberFormat("es-ES", { useGrouping: true }).format(value);
}

export function formatFollowerDelta(value: number): string {
    const formatted = formatFollowers(Math.abs(value));

    if (value > 0) {
        return `+${formatted}`;
    }

    if (value < 0) {
        return `−${formatted}`;
    }

    return formatted;
}

export function weekLabel(isoDate: string): string {
    const date = new Date(`${isoDate}T00:00:00`);
    return new Intl.DateTimeFormat("es", {
        day: "numeric",
        month: "short",
    })
        .format(date)
        .replace(".", "");
}

export function compactWeekLabel(isoDate: string): string {
    const date = new Date(`${isoDate}T00:00:00`);
    const day = String(date.getDate()).padStart(2, "0");
    const month = String(date.getMonth() + 1).padStart(2, "0");
    return `${day}-${month}`;
}

export function historyToChart(items: FollowerHistoryItemResponse[]) {
    return items.map((item) => ({
        label: weekLabel(item.week_start),
        compactLabel: compactWeekLabel(item.week_start),
        value: item.followers_count,
    }));
}

export function disconnectedConnection(): InstagramConnectionResponse {
    return {
        connected: false,
        username: null,
        instagram_account_id: null,
        followers_count: null,
        followers_delta: null,
    };
}

export type InstagramOAuthStatus = "connected" | "error" | undefined;
