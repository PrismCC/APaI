import os
from pathlib import Path

from openai import OpenAI, Stream
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

from log import Log
from message import Message


class Agent:
    def __init__(
        self,
        client: OpenAI,
        api_provider: str,
        model_id: str,
        instr_kv: tuple[str, str],
        context_len: int,
    ) -> None:
        self.client = client
        self.api_provider = api_provider
        self.model_id = model_id
        self.instr_key = instr_kv[0]
        self.instruction = instr_kv[1]
        self.context_len = context_len

        self.log = Log(model_id, instr_kv[0], Path("logs") / f"{model_id}.log")
        self.message = Message(self.instruction)
        self.dialog_count = 0
        self.last_answer = ""

    def add_dialog(self, role: str, content: str) -> None:
        self.message.add_dialog(role, content)
        self.log.write_dialog(role, content)

    def reset_message(self) -> None:
        self.dialog_count = 0
        self.message = Message(self.instruction)
        self.log = Log(
            self.model_id,
            self.instr_key,
            Path("logs") / f"{self.model_id}.log",
        )

    def clean_log(self) -> None:
        self.log.clean()

    def open_log(self) -> bool:
        if self.log.log_path.exists():
            os.startfile(self.log.log_path)  # noqa: S606
            return True
        return False

    def change_log(self, save_path: Path) -> None:
        self.log.save_path = save_path
        self.log.header_written = self.dialog_count > 0

    def get_info_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Provider")
        table.add_column("Model ID")
        table.add_column("Instr Key")
        table.add_column("Context Length")
        table.add_row(
            self.api_provider,
            self.model_id,
            self.instr_key,
            str(self.context_len),
        )
        return table

    def create_stream(self) -> Stream:
        return self.client.chat.completions.create(
            model=self.model_id,
            messages=self.message.generate_messages(self.context_len),
            stream=True,
        )

    def read_stream(self, console: Console, stream: Stream) -> str:
        content_buffer = []
        reasoning_buffer = []
        for chunk in stream:
            if (
                hasattr(chunk.choices[0].delta, "reasoning_content")
                and chunk.choices[0].delta.reasoning_content
            ):
                reasoning_buffer.append(chunk.choices[0].delta.reasoning_content)
                console.print(
                    chunk.choices[0].delta.reasoning_content,
                    style="dim magenta",
                    end="",
                )
            elif chunk.choices[0].delta.content:
                content_buffer.append(chunk.choices[0].delta.content)
                console.print(
                    chunk.choices[0].delta.content,
                    style="cyan",
                    end="",
                )
        return "".join(content_buffer) + "\n"

    def chat(self, ask: str, file: str, console: Console) -> None:
        self.dialog_count += 1
        self.add_dialog("user", file + ask)
        stream = self.create_stream()

        if self.dialog_count < self.context_len:
            console.print(
                f"context: [{self.dialog_count}|{self.context_len}]",
                style="green",
            )
        else:
            console.print(
                f"context: [{self.context_len}|{self.context_len}]"
                f"{self.dialog_count - self.context_len} context(s) expired",
                style="yellow",
            )

        if file == "":
            console.print("user:", style="bold")
            console.print(f"{ask}", style="blue")
        else:
            console.print("user:\n[file content]", style="bold")
            console.print(f"{ask}", style="blue")

        console.print(f"{self.model_id}:", style="bold")

        answer = self.read_stream(console, stream)
        console.print("\n--END--\n", style="yellow")
        self.last_answer = answer

        self.add_dialog("assistant", answer)

    def show_markdown(self, console: Console) -> None:
        if self.last_answer == "":
            console.print("No content to show", style="red")
            return
        console.print("Markdown:\n", style="green")
        console.print(Markdown(self.last_answer))

    def retry(self, console: Console) -> None:
        if self.dialog_count == 0:
            console.print("No dialog to retry", style="red")
            return
        self.message.dialogs.pop()
        self.log.retry()
        stream = self.create_stream()
        console.print(f"{self.model_id}:", style="bold")
        answer = self.read_stream(console, stream)
        console.print("\n--END--\n", style="yellow")
        self.last_answer = answer
        self.add_dialog("assistant", answer)

    def undo(self, console: Console) -> None:
        if self.dialog_count == 0:
            console.print("No dialog to undo", style="red")
            return
        self.message.dialogs.pop()
        self.message.dialogs.pop()
        self.log.undo()
        self.dialog_count -= 1
        if self.dialog_count > 0:
            self.last_answer = self.message.dialogs[-1]["content"]
        else:
            self.last_answer = ""
