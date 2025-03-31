from datetime import datetime
from pathlib import Path


class Log:
    double_line = "=" * 50
    single_line = "-" * 50
    autosave_path = Path("saves") / "autosave.apai"

    def __init__(
        self,
        model_id: str,
        instr_key: str,
        log_path: Path,
        save_path: Path = autosave_path,
    ) -> None:
        self.model_id = model_id
        self.instr_key = instr_key
        self.log_path = log_path
        self.save_path = save_path
        self.header_written = False

    def write_header(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.double_line}\n\n")
            f.write(f"model_id: {self.model_id}\n")
            f.write(f"Instr_key: {self.instr_key}\n\n")
        with self.save_path.open("w", encoding="utf-8") as f:
            f.write(f"{self.model_id}, {self.instr_key}\n")
            f.write("===APaI===\n")

    def write_dialog(self, role: str, content: str) -> None:
        if not self.header_written:
            self.write_header()
            self.header_written = True

        time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.single_line}\n\n")
            f.write(f"{time_string}\n")
            f.write(f"{role}:\n")
            f.write(f"{content.strip()}\n\n")
        with self.save_path.open("a", encoding="utf-8") as f:
            f.write(f"{role}\n")
            f.write(f"{content.strip()}\n")
            f.write("===APaI===\n")

    def clean(self) -> None:
        self.log_path.unlink(missing_ok=True)

    def retry(self) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.single_line}\n\n")
            f.write("[retry]\n\n")
        with self.save_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        delete_count = 0
        one = 1
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "===APaI===":
                if delete_count == one:
                    lines = lines[: i + 1]
                    break
                delete_count += 1
        with self.save_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)

    def undo(self) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(f"{self.single_line}\n\n")
            f.write("[undo]\n\n")
        with self.save_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        delete_count = 0
        two = 2
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "===APaI===":
                if delete_count == two:
                    lines = lines[: i + 1]
                    break
                delete_count += 1
        with self.save_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)
