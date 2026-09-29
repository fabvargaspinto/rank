"use client";

import {
    useEffect,
    useRef,
    useState,
    type ChangeEvent,
} from "react";
import {
    AVATAR_TOO_LARGE_MESSAGE,
    AVATAR_TYPE_MESSAGE,
    isAvatarMimeType,
    MAX_AVATAR_BYTES,
} from "@/lib/domain-limits";
import { prepareAvatar } from "@/lib/prepare-avatar";
import { isObjectUrl } from "@/features/profile/model";

type UseAvatarUploadOptions = {
    initialUrl: string;
    preservedUrl?: string;
};

export function useAvatarUpload({
    initialUrl,
    preservedUrl = "",
}: UseAvatarUploadOptions) {
    const [previewUrl, setPreviewUrl] = useState(initialUrl);
    const [file, setFile] = useState<File | null>(null);
    const previewRef = useRef(previewUrl);
    const preservedRef = useRef(preservedUrl);

    useEffect(() => {
        previewRef.current = previewUrl;
    }, [previewUrl]);

    useEffect(() => {
        preservedRef.current = preservedUrl;
    }, [preservedUrl]);

    useEffect(() => {
        return () => {
            const draft = previewRef.current;

            if (isObjectUrl(draft) && draft !== preservedRef.current) {
                URL.revokeObjectURL(draft);
            }
        };
    }, []);

    function revokeIfDraft(url: string) {
        if (isObjectUrl(url) && url !== preservedRef.current) {
            URL.revokeObjectURL(url);
        }
    }

    async function onFileChange(
        event: ChangeEvent<HTMLInputElement>,
    ): Promise<string | null> {
        const picked = event.target.files?.[0];
        event.target.value = "";

        if (!picked) {
            return null;
        }

        if (!isAvatarMimeType(picked.type)) {
            return AVATAR_TYPE_MESSAGE;
        }

        const prepared = await prepareAvatar(picked);

        if (prepared.size > MAX_AVATAR_BYTES) {
            return AVATAR_TOO_LARGE_MESSAGE;
        }

        const url = URL.createObjectURL(prepared);
        setFile(prepared);

        setPreviewUrl((current) => {
            revokeIfDraft(current);
            return url;
        });

        return null;
    }

    function afterSave(nextPersistedUrl: string) {
        setPreviewUrl((current) => {
            revokeIfDraft(current);
            return nextPersistedUrl;
        });
        setFile(null);
        preservedRef.current = nextPersistedUrl;
    }

    return {
        previewUrl,
        file,
        onFileChange,
        afterSave,
    };
}
