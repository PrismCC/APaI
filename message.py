# 生成对话消息
class Message:
    def __init__(self, instruction: str) -> None:
        self.dialogs: list[dict] = []
        self.instruction: dict = {"role": "system", "content": instruction}

    # role只能为user或者assistant
    def add_dialog(self, role: str, content: str) -> None:
        self.dialogs.append({"role": role, "content": content})

    def generate_messages(self, context_len: int) -> list:
        # dialogs存储的是单次对话 而content_len以一问一答计数 因此要乘二
        return [self.instruction] + self.dialogs[-context_len * 2 :]
