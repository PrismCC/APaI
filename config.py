import json
import difflib

from openai import OpenAI


class ApiBin:
    def __init__(self, name: str, api: str, url: str, models: list[str]):
        self.name = name
        self.api = api
        self.url = url
        self.models = models


class Config:
    def __init__(
        self,
        bins: list[ApiBin],
        instruction_bin: dict,
        api: str,
        url: str,
        model: str,
        instruction_key: str,
        context_len: int,
    ):
        self.bins = bins
        self.instruction_bin = instruction_bin
        self.api = api
        self.url = url
        self.model = model
        self.instruction_key = instruction_key
        self.context_len = context_len

    @classmethod
    def read(cls, bin_path: str, config_path: str, instruction_path: str):
        with open(bin_path, "r", encoding="utf-8") as f:
            bins = json.load(f)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        with open(instruction_path, "r", encoding="utf-8") as f:
            instruction_bin = json.load(f)
        names = bins["names"]
        bin_list = []
        for name in names:
            bin = ApiBin(
                name, bins[name]["api"], bins[name]["url"], bins[name]["models"]
            )
            bin_list.append(bin)
        return Config(
            bin_list,
            instruction_bin,
            config["api"],
            config["url"],
            config["model"],
            config["instruction_key"],
            config["context_len"],
        )

    def get_model_list(self):
        list = []
        for bin in self.bins:
            list.extend(bin.models)
        return list

    def change_model(self, model: str):
        for bin in self.bins:
            if model in bin.models:
                self.model = model
                self.api = bin.api
                self.url = bin.url
                return True
        return False

    def match_model(self, str: str):
        l = difflib.get_close_matches(str, self.get_model_list(), 1, cutoff=0.2)
        if l:
            return l[0]
        return None

    def get_instruction(self):
        return self.instruction_bin[self.instruction_key]

    def change_instruction_key(self, key: str):
        if key in self.instruction_bin:
            self.instruction_key = key
            return True
        return False

    def init_cilent(self):
        return OpenAI(
            api_key=self.api,
            base_url=self.url,
            timeout=1800,
        )

    def save_config(self, path: str):
        dict = {
            "api": self.api,
            "url": self.url,
            "model": self.model,
            "instruction_key": self.instruction_key,
            "context_len": self.context_len,
        }
        json_data = json.dumps(dict, indent=4, ensure_ascii=False)
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_data)

    def __str__(self):
        return f"model: {self.model} \ninstruction_key: {self.instruction_key}\ncontext_len: {self.context_len}"
