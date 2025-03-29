# 生成对话消息
class Message:
    def __init__(self, instruction: str) -> None:
        self.dialogs: list[dict] = []
        self.instruction: dict = {"role": "system", "content": instruction}

    # role只能为user或者assistant
    def add_dialog(self, role: str, content: str) -> None:
        self.dialogs.append({"role": role, "content": content})

    def generate_messages(self, context_len: int) -> list:
        return [self.instruction] + self.dialogs[-context_len:]
