"use client";

type GlobalErrorProps = {
    reset: () => void;
};

export default function GlobalError({ reset }: GlobalErrorProps) {
    return (
        <html lang="es">
            <body
                style={{
                    margin: 0,
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "#010101",
                    color: "#dedede",
                    fontFamily: "Ubuntu, sans-serif",
                    textAlign: "center",
                    padding: "24px",
                }}
            >
                <div>
                    <h1 style={{ fontSize: "2rem", margin: "0 0 12px" }}>
                        No se pudo cargar
                    </h1>
                    <p style={{ margin: "0 0 24px", color: "#a9a8a8" }}>
                        Probá de nuevo en unos segundos.
                    </p>
                    <button
                        type="button"
                        onClick={reset}
                        style={{
                            padding: "12px 20px",
                            border: "none",
                            borderRadius: "8px",
                            background: "#dedede",
                            color: "#010101",
                            font: "inherit",
                            cursor: "pointer",
                        }}
                    >
                        Reintentar
                    </button>
                </div>
            </body>
        </html>
    );
}
