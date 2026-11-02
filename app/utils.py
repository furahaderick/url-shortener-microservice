from nanoid import generate

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MAX_ID_SIZE = 6


def generate_unique_id() -> str:
    unique_id = generate(ALPHABET, size=MAX_ID_SIZE)
    return unique_id
