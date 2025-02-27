class ColorManager:
    ANSI_RED = "\033[91m"
    ANSI_GREEN = "\033[92m"
    ANSI_YELLOW = "\033[93m"
    ANSI_BLUE = "\033[94m"
    ANSI_MAGENTA = "\033[95m"
    ANSI_CYAN = "\033[96m"
    ANSI_RESET = "\033[0m"

    @classmethod
    def red(cls, text):
        return cls.ANSI_RED + str(text) + cls.ANSI_RESET

    @classmethod
    def green(cls, text):
        return cls.ANSI_GREEN + str(text) + cls.ANSI_RESET

    @classmethod
    def yellow(cls, text):
        return cls.ANSI_YELLOW + str(text) + cls.ANSI_RESET

    @classmethod
    def blue(cls, text):
        return cls.ANSI_BLUE + str(text) + cls.ANSI_RESET

    @classmethod
    def magenta(cls, text):
        return cls.ANSI_MAGENTA + str(text) + cls.ANSI_RESET

    @classmethod
    def cyan(cls, text):
        return cls.ANSI_CYAN + str(text) + cls.ANSI_RESET

    @classmethod
    def red_flag(cls):
        return cls.ANSI_RED

    @classmethod
    def green_flag(cls):
        return cls.ANSI_GREEN

    @classmethod
    def yellow_flag(cls):
        return cls.ANSI_YELLOW

    @classmethod
    def blue_flag(cls):
        return cls.ANSI_BLUE

    @classmethod
    def magenta_flag(cls):
        return cls.ANSI_MAGENTA

    @classmethod
    def cyan_flag(cls):
        return cls.ANSI_CYAN

    @classmethod
    def reset_flag(cls):
        return cls.ANSI_RESET
