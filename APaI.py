import datetime
import os
from pathlib import Path
from openai import OpenAI

from colormanager import ColorManager as cm
from config import Config


class Dialog:
    def __init__(self, ask, response, file):
        self.ask = ask
        self.response = response
        self.file = file
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def create_stream(client: OpenAI, model: str, messages: list):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )


def print_stream(stream):
    reasoning_content = ""
    content = ""
    for chunk in stream:
        if (
            hasattr(chunk.choices[0].delta, "reasoning_content")
            and chunk.choices[0].delta.reasoning_content
        ):
            reasoning_content += chunk.choices[0].delta.reasoning_content
            print(cm.magenta(chunk.choices[0].delta.reasoning_content), end="")
        else:
            content += chunk.choices[0].delta.content
            print(cm.blue(chunk.choices[0].delta.content), end="")
    return content


def main():
    config: Config = Config.read("api_bins.json", "config.json", "instructions.json")
    if config is None:
        print("Please configure the config first.")
        return

    client = config.init_client()

    model_name = config.model
    logs_path = "logs"
    log = Log(model_name, logs_path)

    print(cm.cyan(config))

    while True:
        ask = input("> ").strip()
        file = ""
        func = ask.split(" ")[0].lower()
        para = ask.split(" ")[1] if ask.count(" ") > 0 else None

        if func == "exit":
            print(cm.yellow("Bye!"))
            break
        elif func == "reset":
            log.reset()
            print(cm.yellow("Dialogs are reset."))
            continue
        elif func == "clean":
            log.clean()
            print(cm.yellow("Logs are cleaned."))
            continue
        elif func == "m" or func == "model":
            if para is None:
                print(
                    cm.yellow(
                        "Please input model name from:\n"
                        + " ".join(config.get_model_list())
                    )
                )
                print("\n")
                continue
            model_name = config.match_model(para)
            if not model_name:
                print(
                    cm.yellow(
                        "Model not found. "
                        + "Please input model name from:\n"
                        + " ".join(config.get_model_list())
                    )
                )
                print("\n")
                continue
            config.change_model(model_name)

            log = Log(model_name, logs_path)
            config.save_config("config.json")
            print(cm.yellow(f"Model is changed to {model_name}.\n\n"))
            print(cm.cyan(config))
            continue
        elif func == "len":
            if para is None:
                print(cm.yellow("Please input context length."))
                continue
            config.context_len = int(para)
            config.save_config("config.json")
            print(cm.yellow(f"Context length is changed to {para}.\n\n"))
            print(cm.cyan(config))
            continue
        elif func == "log":
            print(f"model {model_name}'s log opened.")
            os.startfile(log.path)
            continue
        elif func == "f" or func == "file":
            in_path = "in.txt"
            if para is not None:
                in_path = para
            if not os.path.exists(in_path):
                with open(in_path, "w", encoding="utf-8") as f:
                    f.write("Please input the question here.")
            os.startfile(in_path)
            ask = input(
                cm.yellow(
                    "Please input the question after reading the file. Input 'exit' to cancel:\n"
                )
            ).strip()
            if ask.lower() == "exit":
                print(cm.yellow("Canceled.\n"))
                continue
            with open(in_path, "r", encoding="utf-8") as f:
                file = f.read()
        elif func == "i" or func == "ins":
            if para is None:
                print(
                    cm.yellow(
                        f"Please input instruction key from:\n{config.instruction_bin.keys()}"
                    )
                )
            elif not config.change_instruction_key(para):
                print(
                    cm.yellow(
                        f"Instruction key not found. "
                        + f"Please input instruction key from:\n{config.instruction_bin.keys()}"
                    )
                )
            else:
                print(
                    cm.yellow(
                        f"Instruction is changed to {para}: {config.get_instruction()}\n\n"
                    )
                )
                config.save_config("config.json")
                print(cm.cyan(config))
            continue
        elif func == "h" or func == "help":
            print(cm.magenta("Commands:"))
            print(cm.magenta("  exit                        :  Exit"))
            print(cm.magenta("  reset                       :  Reset dialogs"))
            print(cm.magenta("  clean                       :  Clean logs"))
            print(cm.magenta("  log                         :  Open log file"))
            print(cm.magenta("  len   + [context length]    :  Change context length"))
            print(cm.magenta("  m/model + [model name]      :  Change model"))
            print(cm.magenta("  i/ins   + [instruction key] :  Set instruction"))
            print(cm.magenta("  f/file  + [file name]       :  Read from file"))
            print(cm.magenta("  h/help                      :  Show help"))
            print(cm.magenta("  [others]                    :  Chat with AI"))
            print("\n")
            continue

        # Maybe the user input a wrong command
        if file == "" and len(ask) < 10:
            confirm = input(
                cm.yellow("Are you sure to send this short message? (y/n) ")
            )
            if confirm.lower() != "y":
                continue

        print(
            "\nUser: " + cm.cyan(f"[{log.num}|{config.context_len}]\n") + cm.green(ask)
        )
        if log.num > config.context_len:
            print(cm.yellow(f"{log.num - config.context_len} dialogs are omitted."))

        message = Message.generate_message(
            log, ask, file, config.context_len, config.get_instruction()
        )
        stream = create_stream(client, config.model, message)
        print(f"\n{model_name}:")
        response = print_stream(stream)
        print(cm.yellow("\n\n--END--\n\n"))
        log.append(Dialog(ask, response, file))
        log.save()


if __name__ == "__main__":
    main()
