import type { Metadata } from "next";
import Link from "next/link";
import LegalDocument from "@/features/legal/legal-document";

export const metadata: Metadata = {
    title: "Términos",
    description: "Términos de uso de Sello Nómada.",
};

export default function page() {
    return (
        <LegalDocument title="Términos de uso" updatedAt="2 de octubre de 2026">
            <section>
                <h2>Aceptación</h2>
                <p>
                    Al crear una cuenta o usar Sello Nómada aceptas estos términos
                    y la{" "}
                    <Link href="/privacidad">Política de privacidad</Link>. Si no
                    estás de acuerdo, no uses el servicio. El servicio se ofrece
                    desde Chile.
                </p>
            </section>

            <section>
                <h2>El servicio</h2>
                <p>
                    Sello Nómada te permite crear un perfil público, publicar
                    contenido y enlaces, y opcionalmente conectar Instagram para
                    ver métricas de seguidores. El servicio se ofrece “tal cual”;
                    puede cambiar, interrumpirse o tener errores.
                </p>
            </section>

            <section>
                <h2>Tu cuenta</h2>
                <ul>
                    <li>Eres responsable de la seguridad de tu acceso.</li>
                    <li>
                        El nombre de usuario debe respetar las reglas del
                        producto y no puede usurpar marcas ni identidades ajenas.
                    </li>
                    <li>
                        Debes tener edad legal para contratar en tu jurisdicción
                        o el consentimiento de tu representante.
                    </li>
                </ul>
            </section>

            <section>
                <h2>Contenido</h2>
                <p>
                    El contenido que publiques (texto, enlaces, avatar) es tuyo.
                    Nos das licencia limitada para alojarlo y mostrarlo en el
                    servicio. No publiques material ilegal, que infrinja derechos
                    de terceros, spam, malware ni contenido que acose a otras
                    personas. Podemos retirar contenido o suspender cuentas que
                    incumplan estas reglas.
                </p>
            </section>

            <section>
                <h2>Instagram</h2>
                <p>
                    La conexión con Instagram es opcional y está sujeta a los
                    términos de Meta. Solo pedimos los permisos necesarios para
                    las métricas que mostramos. Puedes desconectar Instagram en
                    cualquier momento; Meta también puede revocar el acceso.
                </p>
            </section>

            <section>
                <h2>Disponibilidad y responsabilidad</h2>
                <p>
                    No garantizamos disponibilidad continua ni ausencia de
                    errores. En la máxima medida permitida por la ley chilena, no
                    somos responsables por daños indirectos, lucro cesante o
                    pérdida de datos derivados del uso o la imposibilidad de uso
                    del servicio.
                </p>
            </section>

            <section>
                <h2>Ley aplicable</h2>
                <p>
                    Estos términos se rigen por las leyes de la República de
                    Chile. Cualquier controversia se someterá a los tribunales
                    competentes de Chile, sin perjuicio de derechos imperativos
                    del consumidor que te correspondan.
                </p>
            </section>

            <section>
                <h2>Cambios</h2>
                <p>
                    Podemos actualizar estos términos. La fecha de “Última
                    actualización” indica la versión vigente. El uso continuado
                    después de un cambio relevante implica aceptación de la nueva
                    versión.
                </p>
            </section>
        </LegalDocument>
    );
}
