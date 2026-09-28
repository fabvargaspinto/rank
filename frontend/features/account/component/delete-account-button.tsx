"use client";

import { useActionState, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import Button from "@/components/ui/button/button";
import Input from "@/components/ui/input/input";
import { emptyFetchResponse } from "@/lib/fetch_data";
import { deleteAccountAction } from "../action/delete-account-action";
import styles from "./delete-account-button.module.css";

type DeleteAccountButtonProps = {
    username: string;
};

export default function DeleteAccountButton({ username }: DeleteAccountButtonProps) {
    const titleId = useId();
    const inputId = useId();
    const dialogRef = useRef<HTMLDialogElement>(null);
    const [open, setOpen] = useState(false);
    const [confirmation, setConfirmation] = useState("");
    const [state, formAction, pending] = useActionState(
        deleteAccountAction,
        emptyFetchResponse,
    );
    const expected = username.trim().toLowerCase();
    const confirmed =
        expected.length > 0 && confirmation.trim().toLowerCase() === expected;

    useEffect(() => {
        const dialog = dialogRef.current;

        if (!dialog) {
            return;
        }

        if (open && !dialog.open) {
            dialog.showModal();
        }

        if (!open && dialog.open) {
            dialog.close();
        }
    }, [open]);

    function close() {
        if (pending) {
            return;
        }

        setOpen(false);
        setConfirmation("");
    }

    return (
        <>
            <Button
                type="button"
                variant="danger"
                onClick={() => {
                    setConfirmation("");
                    setOpen(true);
                }}
            >
                Borrar cuenta
            </Button>
            {open
                ? createPortal(
                      <dialog
                          ref={dialogRef}
                          className={styles.dialog}
                          aria-labelledby={titleId}
                          onClose={close}
                          onClick={(event) => {
                              if (event.target === event.currentTarget) {
                                  close();
                              }
                          }}
                      >
                          <form
                              className={styles.form}
                              action={formAction}
                              onSubmit={(event) => {
                                  if (!confirmed) {
                                      event.preventDefault();
                                  }
                              }}
                          >
                              <h2 id={titleId} className={styles.title}>
                                  Borrar cuenta
                              </h2>
                              <p className={styles.copy}>
                                  Se borra tu cuenta, tu perfil público y tus
                                  publicaciones. Esta acción no se puede deshacer.
                              </p>
                              <label className={styles.label} htmlFor={inputId}>
                                  Escribí tu usuario para confirmar
                              </label>
                              <Input
                                  id={inputId}
                                  name="confirmation"
                                  value={confirmation}
                                  autoComplete="off"
                                  spellCheck={false}
                                  placeholder={username}
                                  onChange={(event) =>
                                      setConfirmation(event.target.value)
                                  }
                              />
                              {state.isError ? (
                                  <p className={styles.error} role="alert">
                                      {state.message}
                                  </p>
                              ) : null}
                              <div className={styles.actions}>
                                  <Button
                                      type="button"
                                      variant="secondary"
                                      onClick={close}
                                      disabled={pending}
                                  >
                                      Cancelar
                                  </Button>
                                  <Button
                                      type="submit"
                                      variant="danger"
                                      disabled={!confirmed || pending}
                                  >
                                      {pending ? "Borrando..." : "Borrar cuenta"}
                                  </Button>
                              </div>
                          </form>
                      </dialog>,
                      document.body,
                  )
                : null}
        </>
    );
}
