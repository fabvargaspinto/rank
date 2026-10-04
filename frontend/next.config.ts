import type { NextConfig } from "next";

function supabaseStorageOrigin(): string {
    const raw = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").trim();
    if (!raw) {
        return "";
    }

    try {
        return new URL(raw).origin;
    } catch {
        return "";
    }
}

function supabaseAvatarRemotePatterns(): NonNullable<
    NextConfig["images"]
>["remotePatterns"] {
    const patterns: NonNullable<NextConfig["images"]>["remotePatterns"] = [];
    const raw = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").trim();

    if (raw) {
        try {
            const url = new URL(raw);
            const protocol = url.protocol === "http:" ? "http" : "https";
            patterns.push({
                protocol,
                hostname: url.hostname,
                ...(url.port ? { port: url.port } : {}),
                pathname: "/storage/v1/object/public/avatars/**",
            });
        } catch {
            // URL inválida: sin patrón remoto.
        }
    }

    if (process.env.NODE_ENV !== "production") {
        patterns.push({
            protocol: "http",
            hostname: "127.0.0.1",
            port: "54321",
            pathname: "/storage/v1/object/public/avatars/**",
        });
    }

    return patterns;
}

const supabaseOrigin = supabaseStorageOrigin();

const contentSecurityPolicyReportOnly = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://js.hcaptcha.com https://*.hcaptcha.com",
    "style-src 'self' 'unsafe-inline' https://*.hcaptcha.com",
    [
        "img-src 'self' data: blob:",
        supabaseOrigin,
        "https://*.cdninstagram.com",
        "https://*.fbcdn.net",
    ]
        .filter(Boolean)
        .join(" "),
    "connect-src 'self' https://api.hcaptcha.com https://*.hcaptcha.com",
    "frame-src https://newassets.hcaptcha.com https://*.hcaptcha.com",
    "font-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "frame-ancestors 'none'",
    "form-action 'self'",
].join("; ");

const securityHeaders = [
    {
        key: "Strict-Transport-Security",
        value: "max-age=31536000; includeSubDomains",
    },
    { key: "X-Content-Type-Options", value: "nosniff" },
    {
        key: "Referrer-Policy",
        value: "strict-origin-when-cross-origin",
    },
    {
        key: "Permissions-Policy",
        value: "camera=(), microphone=(), geolocation=()",
    },
    { key: "X-Frame-Options", value: "DENY" },
    {
        key: "Content-Security-Policy-Report-Only",
        value: contentSecurityPolicyReportOnly,
    },
];

const nextConfig: NextConfig = {
    output: "standalone",
    reactCompiler: true,
    poweredByHeader: false,
    images: {
        remotePatterns: supabaseAvatarRemotePatterns(),
    },
    experimental: {
        serverActions: {
            bodySizeLimit: "3mb",
        },
    },
    async headers() {
        return [{ source: "/:path*", headers: securityHeaders }];
    },
};

export default nextConfig;
