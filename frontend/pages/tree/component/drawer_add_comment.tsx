import Drawer from "@/ui/drawer/drawer";
import styles from "./drawer_add_comment.module.css";
import Input from "@/ui/input/input";
import Textarea from "@/ui/text-area/text-area";
import Button from "@/ui/button/button";






export default function DrawerAddComment({ open, onClose }: { open: boolean, onClose: () => void }) {
    return (
        <Drawer
            open={open}
            onClose={onClose}
            title="Añadir comentario"
        >
            <form className={styles.container}>
            
                <div className={styles.inputContainer}>
                    <p className={styles.inputDescription}>Escribe tu comentario</p>
                    <Textarea placeholder="Añadir comentario" size="full" name="comment" />
                    <p className={styles.inputError}>Comentario</p>
                </div>
                <div className={styles.inputContainer}>
                <p className={styles.inputDescription}>Link</p>
                <Input type="text" placeholder="Añadir link" name="link" />    
                <p className={styles.inputError}>Comentario</p>
                </div>
                <div className={styles.buttonContainer}>
                    <Button size="md" variant="secondary" onClick={onClose}>Añadir comentario</Button>
                    <p className={styles.inputError}>* Los campos obligatorios</p>
                </div>
            </form>
        </Drawer>
    )
}
