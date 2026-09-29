import { httpsUrlError, MAX_LINKS } from "@/lib/domain-limits";

export type ProfileLink = {
    id: string;
    url: string;
    type?: string;
};

export function isObjectUrl(value: string): boolean {
    return value.startsWith("blob:") || value.startsWith("data:");
}

export function createEmptyLink(id = crypto.randomUUID()): ProfileLink {
    return { id, url: "" };
}

export function linksForEditor(links: ProfileLink[]): ProfileLink[] {
    if (links.length === 0) {
        return [createEmptyLink("link-0")];
    }

    return links.slice(0, MAX_LINKS).map((link, index) => ({
        id: link.id || `link-${index}`,
        url: link.url,
        type: link.type,
    }));
}

export function trimProfileText(value: string): string {
    return value.trim();
}

export type ProfileLinkPayload = { url: string };

export function linksPayload(links: ProfileLink[]): ProfileLinkPayload[] {
    return links
        .map((link) => ({ url: trimProfileText(link.url) }))
        .filter((link) => link.url.length > 0)
        .slice(0, MAX_LINKS);
}

export function firstLinkValidationError(
    links: ProfileLink[],
): string | null {
    const error = linksPayload(links)
        .map((link) => httpsUrlError(link.url))
        .find((message) => message != null);

    return error ?? null;
}
