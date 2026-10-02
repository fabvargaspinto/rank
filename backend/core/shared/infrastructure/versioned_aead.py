import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VERSION_PREFIX = "v1:"


def seal(aes: AESGCM, plaintext: bytes, associated_data: str) -> str:
    nonce = os.urandom(12)
    ciphertext = aes.encrypt(
        nonce,
        plaintext,
        associated_data.encode("utf-8"),
    )
    return VERSION_PREFIX + (nonce + ciphertext).hex()


def open_sealed(aes: AESGCM, sealed: str, associated_data: str) -> bytes:
    if sealed.startswith(VERSION_PREFIX):
        data = bytes.fromhex(sealed[len(VERSION_PREFIX) :])
        aad: bytes | None = associated_data.encode("utf-8")
    else:
        # Ciphertexts previos a v1 (sin prefijo ni AAD).
        data = bytes.fromhex(sealed)
        aad = None

    nonce = data[:12]
    ciphertext = data[12:]
    return aes.decrypt(nonce, ciphertext, aad)
