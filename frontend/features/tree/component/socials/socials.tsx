"use client";

import InstagramPanel from "@/features/instagram/instagram-panel";
import type { InstagramOAuthStatus } from "@/features/instagram/model";
import type {
    FollowerHistoryItemResponse,
    InstagramConnectionResponse,
} from "@/lib/api/types";
import styles from "./socials.module.css";

export default function Socials({
    editable = false,
    oauthStatus,
    initialConnection,
    initialHistory = [],
}: {
    editable?: boolean;
    oauthStatus?: InstagramOAuthStatus;
    initialConnection?: InstagramConnectionResponse;
    initialHistory?: FollowerHistoryItemResponse[];
}) {
    if (!editable) {
        return (
            <p className={styles.empty}>Todavía no hay métricas para mostrar.</p>
        );
    }

    return (
        <div className={styles.socials}>
            <InstagramPanel
                initialConnection={
                    initialConnection ?? {
                        connected: false,
                        username: null,
                        instagram_account_id: null,
                        followers_count: null,
                        followers_delta: null,
                    }
                }
                initialHistory={initialHistory}
                oauthStatus={oauthStatus}
            />
        </div>
    );
}
