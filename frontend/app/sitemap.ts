import type { MetadataRoute } from "next";
import { siteUrl } from "@/lib/site-url";

export default function sitemap(): MetadataRoute.Sitemap {
    const base = siteUrl();
    return [
        {
            url: base,
            changeFrequency: "weekly",
            priority: 1,
        },
        {
            url: `${base}/privacidad`,
            changeFrequency: "yearly",
            priority: 0.3,
        },
        {
            url: `${base}/terminos`,
            changeFrequency: "yearly",
            priority: 0.3,
        },
    ];
}
