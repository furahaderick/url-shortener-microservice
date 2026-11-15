from nanoid import generate

_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MAX_CODE_SIZE = 6


def generate_unique_code() -> str:
    unique_code = generate(_ALPHABET, size=MAX_CODE_SIZE)
    return unique_code
