import os


class Settings:
    dictionary = os.getenv("PYTHOGOREAN_ARUCO_DICTIONARY", "DICT_4X4_250")
    card_size = int(os.getenv("PYTHOGOREAN_CARD_SIZE", "900"))


settings = Settings()
