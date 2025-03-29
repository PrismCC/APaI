from datetime import datetime
from pathlib import Path


class Log:
    double_line = "=" * 50
    single_line = "-" * 50

    def __init__(self, path: Path) -> None:
        self.path = path

    def write_header(self, model_name: str, instr_key: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{self.double_line}\n\n")
            f.write(f"Model: {model_name}\n")
            f.write(f"Instruction: {instr_key}\n\n")

    def write_dialog(self, role: str, content: str) -> None:
        time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"{self.single_line}\n\n")
            f.write(f"{time_string}\n")
            f.write(f"{role}:\n")
            f.write(f"{content}\n\n")

    def clean(self) -> None:
        self.path.unlink(missing_ok=True)
