import difflib
from dataclasses import asdict, dataclass
from pathlib import Path

import tomli_w
import tomllib
from openai import OpenAI

from agent import Agent


@dataclass
class Api:
    api: str
    url: str
    models: list[str]


@dataclass
class Instruction:
    content: str


@dataclass
class Config:
    provider: str
    api: str
    url: str
    model_id: str
    instr_key: str
    context_len: int


class Environment:
    def __init__(self, api_path: Path, instr_path: Path, config_path: Path) -> None:
        with api_path.open("rb") as f:
            self.api_dict = {k: Api(**v) for k, v in tomllib.load(f).items()}
        with instr_path.open("rb") as f:
            self.instr_dict = {k: Instruction(**v) for k, v in tomllib.load(f).items()}
        with config_path.open("rb") as f:
            self.config = Config(**tomllib.load(f))
        self.config_path = config_path
        self.model_id_list = [
            name for api in self.api_dict.values() for name in api.models
        ]
        self.instr_key_list = list(self.instr_dict.keys())

    def match_model_id(self, model_id: str) -> str:
        match_list = difflib.get_close_matches(
            model_id,
            self.model_id_list,
            cutoff=0.2,
        )
        if match_list:
            return match_list[0]
        return ""

    def match_instr_key(self, instr_key: str) -> str:
        match_list = difflib.get_close_matches(
            instr_key,
            self.instr_key_list,
            cutoff=0.2,
        )
        if match_list:
            return match_list[0]
        return ""

    def save_config(self) -> None:
        with self.config_path.open("wb") as f:
            tomli_w.dump(asdict(self.config), f)

    # 修改配置:
    # 1. 修改config
    # 2. 保存config
    # 3. 重建Agent对象(Log Message OpenAI)

    def change_model(self, model_id: str) -> bool:
        if model_id:
            for provider, api in self.api_dict.items():
                if model_id in api.models:
                    self.config.provider = provider
                    self.config.api = api.api
                    self.config.url = api.url
                    self.config.model_id = model_id
                    self.save_config()
                    return True
        return False

    def change_instr_key(self, instr_key: str) -> bool:
        if instr_key:
            self.config.instr_key = instr_key
            self.save_config()
            return True
        return False

    def change_context_len(self, context_len: int) -> None:
        self.config.context_len = context_len
        self.save_config()

    def init_agent(self) -> Agent:
        return Agent(
            OpenAI(
                api_key=self.config.api,
                base_url=self.config.url,
                timeout=1800,
            ),
            self.config.provider,
            self.config.model_id,
            (
                self.config.instr_key,
                self.instr_dict[self.config.instr_key].content,
            ),
            self.config.context_len,
        )

    def config_to_string(self) -> str:
        return (
            f"model: {self.config.model_id}\n"
            f"instruction: {self.config.instr_key}\n"
            f"context length: {self.config.context_len}\n"
        )

    # 保证存档文件存在
    def read_save(self, save_path: Path) -> Agent:
        dialogs = []
        with save_path.open("r", encoding="utf-8") as f:
            model_id, instr_key = f.readline().split(", ")
            model_id = model_id.strip()
            instr_key = instr_key.strip()
            f.readline()
            while True:
                role = f.readline().strip()
                if not role:
                    break
                lines = []
                while True:
                    line = f.readline()
                    if line.strip() == "===APaI===":
                        break
                    lines.append(line)
                dialogs.append(
                    {
                        "role": role,
                        "content": "".join(lines).strip(),
                    },
                )
        self.change_model(model_id)
        self.change_instr_key(instr_key)
        agent = self.init_agent()
        agent.message.dialogs = dialogs
        agent.change_log(save_path)
        return agent
