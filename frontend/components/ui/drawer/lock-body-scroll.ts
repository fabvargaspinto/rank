const LOCK_ATTR = "data-scroll-locked";

function readLockCount() {
    return parseInt(document.body.getAttribute(LOCK_ATTR) || "0", 10) || 0;
}

export function lockBodyScroll() {
    const { body } = document;
    const count = readLockCount();

    body.setAttribute(LOCK_ATTR, String(count + 1));

    return () => {
        const next = readLockCount() - 1;

        if (next <= 0) {
            body.removeAttribute(LOCK_ATTR);
            return;
        }

        body.setAttribute(LOCK_ATTR, String(next));
    };
}
