const MAX_EDGE = 1024;
const WEBP_QUALITY = 0.8;

export async function prepareAvatar(file: File): Promise<File> {
    if (typeof document === "undefined") {
        return file;
    }

    try {
        const bitmap = await createImageBitmap(file);
        const longest = Math.max(bitmap.width, bitmap.height);
        const scale = longest > MAX_EDGE ? MAX_EDGE / longest : 1;
        const width = Math.max(1, Math.round(bitmap.width * scale));
        const height = Math.max(1, Math.round(bitmap.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const context = canvas.getContext("2d");

        if (!context) {
            bitmap.close();
            return file;
        }

        context.drawImage(bitmap, 0, 0, width, height);
        bitmap.close();

        const blob = await new Promise<Blob | null>((resolve) => {
            canvas.toBlob(resolve, "image/webp", WEBP_QUALITY);
        });

        if (!blob || blob.size >= file.size) {
            return file;
        }

        const base = file.name.replace(/\.[^.]+$/, "") || "avatar";
        return new File([blob], `${base}.webp`, { type: "image/webp" });
    } catch {
        return file;
    }
}
