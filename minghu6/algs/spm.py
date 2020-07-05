import random


def random_ascii_char() -> str:
    return bytes([random.randrange(0, 128)]).decode()


def random_ascii_string(length: int) -> str:
    return bytes((map(lambda _: random.randrange(0, 128), range(length)))).decode()
