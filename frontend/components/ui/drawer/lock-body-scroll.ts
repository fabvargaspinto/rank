const LOCK_ATTR = "data-scroll-locked";
const SIZE_VAR = "--removed-body-scroll-bar-size";

function readLockCount() {
    return parseInt(document.body.getAttribute(LOCK_ATTR) || "0", 10) || 0;
}

function getScrollbarGap() {
    const styles = window.getComputedStyle(document.body);
    const marginLeft = Number.parseInt(styles.marginLeft, 10) || 0;
    const marginRight = Number.parseInt(styles.marginRight, 10) || 0;

    return Math.max(
        0,
        window.innerWidth - document.documentElement.clientWidth + marginRight - marginLeft,
    );
}

export function lockBodyScroll() {
    const { body } = document;
    const count = readLockCount();

    if (count === 0) {
        body.style.setProperty(SIZE_VAR, `${getScrollbarGap()}px`);
    }

    body.setAttribute(LOCK_ATTR, String(count + 1));

    return () => {
        const next = readLockCount() - 1;

        if (next <= 0) {
            body.removeAttribute(LOCK_ATTR);
            body.style.removeProperty(SIZE_VAR);
            return;
        }

        body.setAttribute(LOCK_ATTR, String(next));
    };
}
