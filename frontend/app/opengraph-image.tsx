import { ImageResponse } from "next/og";

export const alt = "Sello Nómada";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
    return new ImageResponse(
        (
            <div
                style={{
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    background: "#010101",
                    color: "#dedede",
                    padding: "80px",
                }}
            >
                <div style={{ fontSize: 72, fontWeight: 700 }}>Sello Nómada</div>
                <div style={{ marginTop: 24, fontSize: 32, color: "#a9a8a8" }}>
                    Tu perfil de artista con todos tus links en un solo lugar.
                </div>
            </div>
        ),
        { ...size },
    );
}
