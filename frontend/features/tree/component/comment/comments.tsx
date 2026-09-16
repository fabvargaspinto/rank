"use client";

import Avatar from "@/components/ui/avatar/avatar";
import styles from "./comments.module.css";

export type Comment = {
    id: number;
    avatar: string;
    user: string;
    date: string;
    text: string;
    link?: string;
};

export const INITIAL_COMMENTS: Comment[] = [
    {
        id: 1,
        avatar: "https://github.com/shadcn.png",
        user: "John Doe",
        date: "2021-01-01",
        text: "Me encantó el último tema. ¿Vas a pasar por Madrid este verano?",
        link: "https://www.google.com",
    },
    {
        id: 2,
        avatar: "https://github.com/shadcn.png",
        user: "Jane Doe",
        date: "2021-01-02",
        text: "Hermosa sesión. Gracias por compartirla.",
    },
    {
        id: 3,
        avatar: "https://github.com/shadcn.png",
        user: "John Doe",
        date: "2021-01-03",
        text: "Me encantó el último tema. ¿Vas a pasar por Madrid este verano?",
        link: "https://www.google.com",
    },
    {
        id: 4,
        avatar: "https://github.com/shadcn.png",
        user: "María Sol",
        date: "2021-01-04",
        text: "Qué producción tan limpia. Lo escuché tres veces seguidas.",
    },
    {
        id: 5,
        avatar: "https://github.com/shadcn.png",
        user: "Alex Ruiz",
        date: "2021-01-05",
        text: "Las armonías del estribillo se quedan en la cabeza.",
        link: "https://www.youtube.com",
    },
    {
        id: 6,
        avatar: "https://github.com/shadcn.png",
        user: "Lucía Vega",
        date: "2021-01-06",
        text: "Ojalá pases por Barcelona también. Un abrazo.",
    },
];

function formatCommentDate(value: string): string {
    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("es", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(date);
}

function hostnameFromUrl(url: string): string {
    try {
        return new URL(url).hostname.replace(/^www\./, "");
    } catch {
        return url;
    }
}

export default function Comments({ comments }: { comments: Comment[] }) {
    if (comments.length === 0) {
        return <p className={styles.empty}>Todavía no hay comentarios.</p>;
    }

    return (
        <ul className={styles.feed} aria-label="Comentarios">
            {comments.map((comment) => (
                <li key={comment.id}>
                    <CommentItem {...comment} />
                </li>
            ))}
        </ul>
    );
}

function CommentItem({ avatar, user, date, text, link }: Omit<Comment, "id">) {
    return (
        <article className={styles.comment}>
            <Avatar src={avatar} name={user} size="sm" />
            <div className={styles.body}>
                <div className={styles.meta}>
                    <p className={styles.user}>{user}</p>
                    <time className={styles.date} dateTime={date}>
                        {formatCommentDate(date)}
                    </time>
                </div>
                <p className={styles.text}>{text}</p>
                {link ? (
                    <a
                        href={link}
                        className={styles.link}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {hostnameFromUrl(link)}
                    </a>
                ) : null}
            </div>
        </article>
    );
}
