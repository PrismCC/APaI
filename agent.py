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

        self.log = Log(Path("logs") / f"{model_id}.log")
        self.message = Message(self.instruction)
        self.dialog_count = 0

        self.log.write_header(model_id, self.instr_key)

    def add_dialog(self, role: str, content: str) -> None:
        self.dialog_count += 1
        self.message.add_dialog(role, content)
        self.log.write_dialog(role, content)

    def reset_message(self) -> None:
        self.dialog_count = 0
        self.message = Message(self.instruction)
        self.log = Log(Path("log") / f"{self.model_id}.log")
        self.log.write_header(self.model_id, self.instruction)

    def clean_log(self) -> None:
        self.log.clean()

    def open_log(self) -> bool:
        if self.log.path.exists():
            os.startfile(self.log.path)  # noqa: S606
            return True
        return False

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
        self.add_dialog("user", file + "/n" + ask)
        stream = self.create_stream()
        answer = ""

        if self.dialog_count < self.context_len:
            console.print(
                f"context: [{self.dialog_count}|{self.context_len}]",
                style="cyan",
            )
        else:
            console.print(
                f"context: [{self.context_len}|{self.context_len}]"
                f"{self.dialog_count - self.context_len} context(s) expired",
                style="yellow",
            )

        if file == "":
            console.print(f"user:\n{ask}", style="blue")
        else:
            console.print(f"user:\n[file content]\n{ask}", style="blue")

        console.print(f"{self.model_id}:", style="cyan")

        answer = self.read_stream(console, stream)
        console.print("\n\nMarkdown:\n", style="green")
        console.print(Markdown(answer))
        self.add_dialog("assistant", answer)
