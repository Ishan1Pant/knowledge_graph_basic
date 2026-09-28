import json
import os
from typing import Any

from .retrieval import validate_plan


class PlannerConfigurationError(RuntimeError):
    """Raised when the OpenAI planner has not been configured with an API key."""


class OpenAIPlanner:
    """Use OpenAI to map a question to a constrained, validated graph plan."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None

    def plan(self, question: str) -> dict[str, Any]:
        if not self.api_key:
            raise PlannerConfigurationError(
                "OPENAI_API_KEY is required to answer questions."
            )

        if self.client is None:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)

        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Convert the user's e-commerce question into a JSON object "
                        "with exactly these optional fields: filters and search. "
                        "filters may contain only brand, vendor, category, name, "
                        "each with a string value. search is a string. Use exact "
                        "entity values mentioned by the user. Do not write SQL, "
                        "Cypher, code, or answer the question. Return {} when no "
                        "specific filter or search term can be identified."
                    ),
                },
                {"role": "user", "content": question},
            ],
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty query plan.")
        return validate_plan(json.loads(content))