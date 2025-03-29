import os
from collections.abc import Generator
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
        model_name: str,
        instr_kv: tuple[str, str],
        context_len: int,
    ) -> None:
        self.client = client
        self.api_provider = api_provider
        self.model_name = model_name
        self.instr_key = instr_kv[0]
        self.instruction = instr_kv[1]
        self.context_len = context_len

        self.log = Log(Path("log") / f"{model_name}.log")
        self.message = Message(self.instruction)
        self.dialog_count = 0

        self.log.write_header(model_name, self.instr_key)

    def add_dialog(self, role: str, content: str) -> None:
        self.dialog_count += 1
        self.message.add_dialog(role, content)
        self.log.write_dialog(role, content)

    def reset_message(self) -> None:
        self.dialog_count = 0
        self.message = Message(self.instruction)
        self.log = Log(Path("log") / f"{self.model_name}.log")
        self.log.write_header(self.model_name, self.instruction)

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
        table.add_column("Model Name")
        table.add_column("Instr Key")
        table.add_column("Context Length")
        table.add_row(
            self.api_provider,
            self.model_name,
            self.instr_key,
            str(self.context_len),
        )
        return table

    def create_stream(self) -> Stream:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=self.message.generate_messages(self.context_len),
            stream=True,
        )

    def read_stream(self, stream: Stream) -> Generator[dict, None, str]:
        content = ""
        for chunk in stream:
            if (
                hasattr(chunk.choices[0].delta, "reasoning_content")
                and chunk.choices[0].delta.reasoning_content
            ):
                yield {
                    "type": "reasoning",
                    "content": chunk.choices[0].delta.reasoning_content,
                }
            elif chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                yield {
                    "type": "content",
                    "content": chunk.choices[0].delta.content,
                }
        return content

    def chat(self, ask: str, file: str, console: Console) -> None:
        self.add_dialog("user", file + "/n" + ask)
        stream = self.create_stream()
        generator = self.read_stream(stream)
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

        console.print(f"{self.model_name}: ", style="cyan")

        try:
            while True:
                response = next(generator)
                if response["type"] == "reasoning":
                    console.print(response["content"], style="dim magenta")
                elif response["type"] == "content":
                    console.print(Markdown(response["content"]))
        except StopIteration as e:
            answer = e.value

        self.add_dialog("assistant", answer)
