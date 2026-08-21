import Button from '@/ui/button/button';
import styles from './hero.module.css';

export default function Hero() {
    return (
        <div className={styles.hero}>
        <div className={styles.heroCopy}>
        <h1 className={styles.heroTitle}>Sello <span className={styles.heroTitleHighlight}>Nomada</span></h1>
        <p className={styles.heroDescription}>Comunidad de artistas, músicos y creadores digitales</p>
        </div>
        <div className={styles.heroButtons}>
        <Button variant="primary" size="full">Registrarse</Button>
        <Button variant="secondary" size="full">Iniciar sesión</Button>
        </div>


        </div>
    );
}