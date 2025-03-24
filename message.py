class Message:
    def __init__(self):
        self.messages = []

    def add_dialog(self, dialog):
        if dialog.file != "":
            self.messages.append(
                {
                    "role": "user",
                    "content": dialog.file,
                }
            )
        self.messages.append(
            {
                "role": "user",
                "content": dialog.ask,
            }
        )
        self.messages.append(
            {
                "role": "assistant",
                "content": dialog.response,
            }
        )

    def add_ask(self, ask):
        self.messages.append(
            {
                "role": "user",
                "content": ask,
            }
        )

    def add_instruction(self, instruction):
        self.messages.append(
            {
                "role": "system",
                "content": instruction,
            }
        )

    def add_file(self, file):
        self.messages.append(
            {
                "role": "user",
                "content": file,
            }
        )

    def get_messages(self):
        return self.messages

    @classmethod
    def generate_message(
        cls, log, ask: str, file: str, context_len: int, instruction: str = ""
    ):
        message = Message()
        if instruction:
            message.add_instruction(instruction)
        start_index = log.num - context_len if log.num > context_len else 0
        for i in range(start_index, log.num):
            dialog = log.data[i]
            message.add_dialog(dialog)
        if file != "":
            message.add_file(file)
        message.add_ask(ask)
        return message.get_messages()
