from pathlib import Path


class Log:
    def __init__(self, name, dir_path):
        self.name = name
        self.dir = dir_path
        self.path = f"{dir_path}\\{name}.log"
        self.data = []
        self.num = 0
        self.pointer = 0

    def save(self):
        dir_path = Path(self.dir)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)

        with open(self.path, "a", encoding="utf-8") as f:
            for i in range(self.pointer, self.num):
                dialog = self.data[i]
                if dialog.file != "":
                    f.write(
                        f"{dialog.time}\n\nFile:\n{dialog.file}\n\nUser:\n{dialog.ask}\n\n{self.name}:\n{dialog.response}\n\n--------------------------------\n\n"
                    )
                else:
                    f.write(
                        f"{dialog.time}\n\nUser:\n{dialog.ask}\n\n{self.name}:\n{dialog.response}\n\n--------------------------------\n\n"
                    )
        self.pointer = self.num

    def reset(self):
        self.save()
        self.data = []
        self.num = 0
        self.pointer = 0

    def clean(self):
        self.data = []
        self.num = 0
        self.pointer = 0
        with open(self.path, "w") as f:
            pass

    def append(self, dialog):
        self.data.append(dialog)
        self.num += 1
