import type { Metadata } from "next";
import LegalDocument from "@/features/legal/legal-document";

export const metadata: Metadata = {
    title: "Privacidad",
    description: "Política de privacidad de Sello Nómada.",
};

export default function page() {
    return (
        <LegalDocument title="Política de privacidad" updatedAt="2 de octubre de 2026">
            <section>
                <h2>Quiénes somos</h2>
                <p>
                    Sello Nómada (“nosotros”) opera el sitio y la aplicación donde
                    creas un perfil público, publicas contenido y, si quieres,
                    conectas una cuenta de Instagram para ver métricas de
                    seguidores. Este documento describe qué datos tratamos, para
                    qué, dónde se guardan y cómo puedes ejercer tus derechos.
                    El responsable del tratamiento es Sello Nómada, con
                    operaciones en Chile.
                </p>
            </section>

            <section>
                <h2>Qué datos guardamos</h2>
                <ul>
                    <li>
                        <strong>Cuenta.</strong> Email (cifrado en reposo),
                        proveedor de acceso (email o Google) e identificadores
                        técnicos de sesión.
                    </li>
                    <li>
                        <strong>Perfil.</strong> Nombre de usuario, nombre para
                        mostrar, descripción, avatar y enlaces que cargues.
                    </li>
                    <li>
                        <strong>Publicaciones.</strong> Texto, enlaces y metadatos
                        de las publicaciones de tu perfil.
                    </li>
                    <li>
                        <strong>Instagram (opcional).</strong> Si conectas
                        Instagram: identificador de la cuenta, usuario, foto de
                        perfil (URL), token de acceso cifrado e historial de
                        conteos de seguidores por semana.
                    </li>
                    <li>
                        <strong>Registros técnicos.</strong> Logs de servidor
                        necesarios para operar y diagnosticar fallos (sin guardar
                        contraseñas ni tokens en claro).
                    </li>
                </ul>
            </section>

            <section>
                <h2>Para qué los usamos</h2>
                <ul>
                    <li>Crear y mantener tu cuenta y tu perfil público.</li>
                    <li>Mostrar tus publicaciones y enlaces a quien visite tu URL.</li>
                    <li>
                        Si conectas Instagram, renovar el acceso y actualizar
                        métricas de seguidores.
                    </li>
                    <li>Enviarte emails de confirmación o recuperación de acceso.</li>
                    <li>Cumplir obligaciones legales y pedidos de borrado.</li>
                </ul>
            </section>

            <section>
                <h2>Dónde se almacenan</h2>
                <p>
                    Los datos de cuenta, perfil y publicaciones viven en{" "}
                    <strong>Supabase</strong> (PostgreSQL y Storage). Los datos de
                    Instagram Analytics viven en <strong>Turso</strong>. Cada
                    servicio corre en la región que configuremos para el proyecto;
                    los proveedores pueden procesar datos fuera de Chile según
                    sus propios términos.
                </p>
            </section>

            <section>
                <h2>Por cuánto tiempo</h2>
                <p>
                    Conservamos los datos mientras tu cuenta exista. Si borras la
                    cuenta o desconectas Instagram, eliminamos el perfil, las
                    publicaciones asociadas, la conexión de Instagram y el
                    historial de seguidores vinculados. Los backups de los
                    proveedores pueden retener copias por un tiempo limitado según
                    su política.
                </p>
            </section>

            <section>
                <h2>Cómo borrar o limitar el uso</h2>
                <ul>
                    <li>
                        Desde la app puedes borrar tu cuenta: eso elimina perfil,
                        avatar, publicaciones e identidad de acceso, y desconecta
                        Instagram.
                    </li>
                    <li>
                        Puedes desconectar solo Instagram sin borrar el resto del
                        perfil.
                    </li>
                    <li>
                        Si quitas la app en Instagram o pides el borrado de datos
                        a Meta, procesamos sus callbacks y borramos la conexión y
                        los snapshots asociados.
                    </li>
                </ul>
            </section>

            <section>
                <h2>Terceros</h2>
                <p>
                    Usamos Supabase (auth, base y storage), Turso (métricas de
                    Instagram), Meta/Instagram (si conectas la cuenta), Google (si
                    inicias sesión con Google) y el proveedor de correo que
                    configuremos para Auth. Cada uno trata datos según su propia
                    política.
                </p>
            </section>

            <section>
                <h2>Base legal y Chile</h2>
                <p>
                    Tratamos estos datos para prestar el servicio que pides al
                    registrarte y, cuando corresponde, para cumplir obligaciones
                    legales. En Chile aplica la Ley N° 19.628 sobre Protección de
                    la Vida Privada y la normativa vigente en materia de datos
                    personales. Este texto no es asesoramiento legal; si necesitas
                    una evaluación formal, consulta a un abogado.
                </p>
            </section>

            <section>
                <h2>Contacto</h2>
                <p>
                    Para consultas sobre privacidad, usa el canal de contacto
                    publicado en el sitio o el email de soporte que indiquemos al
                    momento del lanzamiento.
                </p>
            </section>
        </LegalDocument>
    );
}
