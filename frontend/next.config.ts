import type { NextConfig } from "next";

function supabaseStorageOrigin(): string {
    const raw = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").trim();
    if (!raw) {
        return "https://*.supabase.co";
    }

    try {
        return new URL(raw).origin;
    } catch {
        return "https://*.supabase.co";
    }
}

const contentSecurityPolicyReportOnly = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    `img-src 'self' data: blob: ${supabaseStorageOrigin()} https://*.cdninstagram.com https://*.fbcdn.net`,
    "connect-src 'self'",
    "font-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "frame-ancestors 'none'",
    "form-action 'self'",
].join("; ");

const securityHeaders = [
    {
        key: "Strict-Transport-Security",
        value: "max-age=604800; includeSubDomains",
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
