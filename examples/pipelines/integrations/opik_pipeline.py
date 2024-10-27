"""
title: Comet Opik Integration Pipeline
author: TheCodingSheikh
date: 2024-10-27
version: 1.0
license: MIT
description: A pipeline for integrating opik.
requirements: opik
"""


from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel
from openai import OpenAI
from opik.integrations.openai import track_openai

import os
import requests

import opik

os.environ["OPIK_BASE_URL"] = "http://opik-frontend:5173/api"
opik.configure(use_local=False)

class Pipeline:
    class Valves(BaseModel):
        OPENAI_API_BASE_URL: str = "http://open-webui-ollama:11434/v1"
        OPENAI_API_KEY: str = "ollama"
        pass

    def __init__(self):
        self.type = "manifold"
        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "openai_pipeline"
        self.name = "OpenAI: "

        self.valves = self.Valves(
            **{
                "OPENAI_API_KEY": os.getenv(
                    "OPENAI_API_KEY", "ollama"
                )
            }
        )

        self.client = OpenAI(
            base_url=self.valves.OPENAI_API_BASE_URL,
            api_key=self.valves.OPENAI_API_KEY,
        )
        self.client  = track_openai(self.client)

        self.pipelines = self.get_openai_models()
        pass

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        # This function is called when the valves are updated.
        print(f"on_valves_updated:{__name__}")
        self.pipelines = self.get_openai_models()
        pass


    def get_openai_models(self):
        if self.valves.OPENAI_API_KEY:
            try:

                models = self.client.models.list()
                return [
                    {
                        "id": model.id,
                        "name": model.id,
                    }
                    for model in models
                ]

            except Exception as e:

                print(f"Error: {e}")
                return [
                    {
                        "id": "error",
                        "name": "Could not fetch models from OpenAI, please update the API Key in the valves.",
                    },
                ]
        else:
            return []

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom pipelines like RAG.
        print(f"pipe:{__name__}")
        print(f"MMMMM:{messages}")
        print(f"UUUUU:{user_message}")

        # headers = {}
        # headers["Authorization"] = f"Bearer {self.valves.OPENAI_API_KEY}"
        # headers["Content-Type"] = "application/json"

        payload = {**body, "model": model_id}
        print(f"BBBBBBB{body}")
        if "user" in payload:
            del payload["user"]
        if "chat_id" in payload:
            del payload["chat_id"]
        if "title" in payload:
            del payload["title"]

        print(payload)
        print(f"PPPPPPP:{payload}")

        # try:
            # r = requests.post(
            #     url=f"{self.valves.OPENAI_API_BASE_URL}/chat/completions",
            #     json=payload,
            #     headers=headers,
            #     stream=True,
            # )
        r = self.client.chat.completions.create(
            model = model_id,
            messages = body["messages"] ,
            stream = body["stream"]
        )

        return r
