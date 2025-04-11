from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.text import Text

from environment import Environment


def main_loop(console: Console, env: Environment) -> None:  # noqa: C901, PLR0915
    agent = env.init_agent()
    console.print(agent.get_info_table())

    def exit_program() -> None:
        console.print("Bye!", style="bold green")
        sys.exit(0)

    def help_message() -> None:
        console.print("Help    message:", style="bold green")
        console.print("exit:   Exit the program", style="bold green")
        console.print("reset:  Reset agent's memory", style="bold green")
        console.print("retry:  Retry the last question", style="bold green")
        console.print("undo:   Undo the last question", style="bold green")
        console.print("log:    Open log file", style="bold green")
        console.print("clean:  Clean log file", style="bold green")
        console.print("save:   Save the current conversation", style="bold green")
        console.print("load:   Load a previous conversation", style="bold green")
        console.print("model:  Change the model", style="bold green")
        console.print("instr:  Change the instruction", style="bold green")
        console.print("length: Change the context length", style="bold green")
        console.print("file:   Input file content", style="bold green")
        console.print("md:     Render last output as markdown", style="bold green")
        console.print("help:   Show this help message", style="bold green")
        console.print("others: Send a message to the agent", style="bold green")
        console.print(
            "Note: If your first line is empty, multi-line mode will be enabled.",
            style="dim green",
        )
        console.print(
            "      In this mode, you should end your input with a blank line.",
            style="dim green",
        )

    def reset_agent() -> None:
        agent.reset_message()
        console.print("Agent's memory has been reset.", style="green")

    def retry() -> None:
        agent.retry(console)

    def undo() -> None:
        agent.undo(console)
        console.print("Last dialog undone.", style="green")

    def open_log() -> None:
        if agent.open_log():
            console.print("Log file opened.", style="green")
        else:
            console.print("Log file not found.", style="red")

    def clean_log() -> None:
        agent.clean_log()
        console.print("Log file cleaned.", style="green")

    def change_model(model_id: str) -> None:
        nonlocal agent
        model_id = env.match_model_id(model_id)
        if env.change_model(model_id):
            console.print(f"Model changed to {model_id}.", style="green")
            agent = env.init_agent()
            console.print(agent.get_info_table())
        else:
            console.print("Model not found, please try again.", style="red")

    def change_instr(instr_key: str) -> None:
        nonlocal agent
        instr_key = env.match_instr_key(instr_key)
        if env.change_instr_key(instr_key):
            console.print(f"Instruction changed to {instr_key}.", style="green")
            agent = env.init_agent()
            console.print(agent.get_info_table())
        else:
            console.print("Instruction not found, please try again.", style="red")

    def change_context_len(context_len: int) -> None:
        nonlocal agent
        env.change_context_len(context_len)
        agent = env.init_agent()
        console.print(f"Context length changed to {context_len}.", style="green")
        console.print(agent.get_info_table())

    def save(save_name: str) -> None:
        nonlocal agent
        save_path = Path("saves") / f"{save_name}.apai"
        old_path = agent.log.save_path
        shutil.copy(old_path, save_path)
        agent.change_log(save_path)
        console.print(f"Conversation saved to {save_path}.", style="green")

    def load(save_name: str) -> None:
        nonlocal agent
        save_path = Path("saves") / f"{save_name}.apai"
        if not save_path.exists():
            console.print(f"Save file {save_path} does not exist.", style="red")
            return
        agent = env.read_save(save_path)
        console.print(f"Conversation loaded from {save_path}.", style="green")
        console.print(agent.get_info_table())
        if agent.dialog_count > 0:
            console.print("last dialog:", style="dim green")
            console.print(f"{agent.message.dialogs[-2]['role']:}", style="dim bold")
            console.print(f"{agent.message.dialogs[-2]['content']}", style="dim blue")
            console.print(f"{agent.message.dialogs[-1]['role']:}", style="dim bold")
            console.print(f"{agent.message.dialogs[-1]['content']}", style="dim cyan")

    def show_markdown(console: Console) -> None:
        agent.show_markdown(console)

    def get_file_input(file_path: Path = Path(".in.txt")) -> tuple[str, str]:
        if not file_path.exists():
            if file_path == Path(".in.txt"):
                file_path.touch()
            else:
                console.print(f"File {file_path} does not exist.", style="red")
                return "", ""
        os.startfile(file_path)  # noqa: S606
        console.print(
            f"{file_path} opened, input your content here and save it\n",
            style="green",
        )
        terminal_input = console.input(
            Text(
                "You can add some content in terminal and press Enter to continue\n",
                style="dim green",
            ),
        )
        with file_path.open("r", encoding="utf-8") as f:
            file_content = f.read()
        return file_content, terminal_input

    def get_multi_line_input() -> str:
        console.print("[Multi-line mode]\n", style="magenta", end="")
        lines = []
        while True:
            line = console.input()
            if line.strip() == "":
                break
            lines.append(line)
        return "\n".join(lines)

    def check_input(input_str: str) -> bool:
        if input_str.strip() == "":
            return False
        short_text_threshold = 10
        if len(input_str) < short_text_threshold:
            if input_str[0] == " ":
                input_str = input_str[1:]
            else:
                confirm = (
                    console.input(
                        Text(
                            "Are you sure you want to send this short message? (y/n): ",
                            style="bold yellow",
                        ),
                    )
                    .strip()
                    .lower()
                )
                return confirm == "y"
        return True

    command_map = {
        "exit": lambda: exit_program(),
        "help": lambda: help_message(),
        "reset": lambda: reset_agent(),
        "retry": lambda: retry(),
        "undo": lambda: undo(),
        "log": lambda: open_log(),
        "clean": lambda: clean_log(),
        "save": lambda name: save(name),
        "load": lambda name: load(name),
        "model": lambda name: change_model(name),
        "instr": lambda key: change_instr(key),
        "length": lambda length: change_context_len(int(length)),
        "md": lambda: show_markdown(console),
    }

    while True:
        ask = ""
        file = ""
        user_input = console.input("> ")
        if user_input.strip() == "":
            ask = get_multi_line_input()
        else:
            cmd, *args = user_input.split()
            cmd = cmd.lower()
            if cmd in command_map:
                try:
                    command_map[cmd](*args)
                except TypeError:
                    console.print(f"Invalid arguments for command '{cmd}'", style="red")
                    if cmd == "model":
                        console.print("Available models:", style="yellow")
                        console.print(env.model_id_list)
                    elif cmd == "instr":
                        console.print("Available instructions:", style="yellow")
                        console.print(env.instr_key_list)
                continue
            if cmd == "file":
                file, ask = get_file_input(Path(args[0]) if args else Path(".in.txt"))
                if file == "" and ask == "":
                    continue
                file += "\n"
            else:
                ask = user_input
        if file or check_input(ask):
            agent.chat(ask, file, console)


def main() -> None:
    console = Console()
    console.print("This is APaI v0.2.0", style="bold green")
    console.print("Type 'help' for help, or read README.md.", style="dim green")

    api_path = Path("api_bin.toml")
    instr_path = Path("instr_bin.toml")
    config_path = Path("config.toml")
    env = Environment(api_path, instr_path, config_path)

    # 检查配置文件
    if env.model_id_list == []:
        console.print("No model found in api_bin.toml", style="red")
        console.print("Read the README.md file for more information.", style="red")
        return
    while env.config.model_id == "":
        console.print("Please select a model from the following list:", style="yellow")
        console.print(env.model_id_list)
        model_id = console.input("Model ID: ")
        if not env.change_model(env.match_model_id(model_id)):
            console.print("Model not found, please try again.", style="yellow")

    main_loop(console, env)


if __name__ == "__main__":
    main()
