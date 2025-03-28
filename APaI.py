from __future__ import annotations

import os
import sys
from pathlib import Path

from rich.console import Console

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
        console.print("log:    Open log file", style="bold green")
        console.print("clean:  Clean log file", style="bold green")
        console.print("save:   Save the current conversation", style="bold green")
        console.print("load:   Load a previous conversation", style="bold green")
        console.print("model:  Change the model", style="bold green")
        console.print("instr:  Change the instruction", style="bold green")
        console.print("length: Change the context length", style="bold green")
        console.print("file:   Input file content", style="bold green")
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
        console.print("Agent's memory has been reset.", style="cyan")

    def open_log() -> None:
        if agent.open_log():
            console.print("Log file opened.", style="cyan")
        else:
            console.print("Log file not found.", style="red")

    def clean_log() -> None:
        agent.clean_log()
        console.print("Log file cleaned.", style="cyan")

    def change_model(model_name: str) -> None:
        nonlocal agent
        model_name = env.match_model_name(model_name)
        if env.change_model(model_name):
            console.print(f"Model changed to {model_name}.", style="cyan")
            agent = env.init_agent()
            console.print(agent.get_info_table())
        else:
            console.print("Model not found, please try again.", style="red")

    def change_instr(instr_key: str) -> None:
        nonlocal agent
        instr_key = env.match_instr_key(instr_key)
        if env.change_instr_key(instr_key):
            console.print(f"Instruction changed to {instr_key}.", style="cyan")
            agent = env.init_agent()
            console.print(agent.get_info_table())
        else:
            console.print("Instruction not found, please try again.", style="red")

    def change_context_len(context_len: int) -> None:
        nonlocal agent
        env.change_context_len(context_len)
        agent = env.init_agent()
        console.print(f"Context length changed to {context_len}.", style="cyan")
        console.print(agent.get_info_table())

    def get_file_input(file_path: Path = Path(".in.txt")) -> tuple[str, str]:
        if not file_path.exists():
            if file_path == Path(".in.txt"):
                file_path.touch()
            else:
                console.print(f"File {file_path} does not exist.", style="red")
                return "", ""
        os.startfile(file_path)  # noqa: S606
        terminal_input = console.input(
            f"{file_path} opened, input your content here and save it\n"
            "You can also add some content in terminal and press Enter to continue",
        )
        with file_path.open("r", encoding="utf-8") as f:
            file_content = f.read()
        return file_content, terminal_input

    def get_multi_line_input() -> str:
        console.print("[Multi-line mode]", style="magenta")
        lines = []
        while True:
            line = console.input()
            if line.strip() == "":
                break
            lines.append(line)
        return "\n".join(lines)

    command_map = {
        "exit": lambda: exit_program(),
        "help": lambda: help_message(),
        "reset": lambda: reset_agent(),
        "log": lambda: open_log(),
        "clean": lambda: clean_log(),
        "model": lambda name: change_model(name),
        "instr": lambda key: change_instr(key),
        "length": lambda length: change_context_len(int(length)),
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
                continue
            if cmd == "file":
                file, ask = get_file_input(Path(args[0]) if args else Path(".in.txt"))
                if file == "" and ask == "":
                    continue
            else:
                ask = user_input
        if ask:
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
    if env.model_name_list == []:
        console.print("No model found in api_bin.toml", style="red")
        console.print("Read the README.md file for more information.", style="red")
        return
    while env.config.model_name == "":
        console.print("Please select a model from the following list:", style="yellow")
        console.print(env.model_name_list)
        model_name = console.input("Model name: ")
        if not env.change_model(env.match_model_name(model_name)):
            console.print("Model not found, please try again.", style="yellow")

    main_loop(console, env)


if __name__ == "__main__":
    main()
