import Button from "@/components/ui/button/button";
import PageWrapper from "@/components/ui/page-wrapper/page-wrapper";
import Link from "next/link";
import styles from "./empty-tree.module.css";

export default function EmptyTree() {
    return (
        <PageWrapper>
            <section className={styles.container}>
              <h1 className={styles.title}>Árbol vacío</h1>
                <p className={styles.description}>El usuario no se ha encontrado en el sistema</p>

                    <Link href="/" className={styles.button}>
                    <Button variant="primary">
                        Volver al inicio
                    </Button>
                    </Link>
                
            </section>
        </PageWrapper>
    );
}