import json
import os
from typing import Any

from .retrieval import validate_plan


class PlannerConfigurationError(RuntimeError):
    """Raised when the Groq planner has not been configured with an API key."""


class PlannerUnavailableError(RuntimeError):
    """Raised when Groq is temporarily unable to process a request."""


class PlannerModelError(RuntimeError):
    """Raised when the configured Groq model is unavailable to the account."""


class GroqPlanner:
    """Use Groq to map a question to a constrained, validated graph plan."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.model = model or os.environ.get(
            "GROQ_MODEL", "openai/gpt-oss-20b"
        )
        self.client = None

    def plan(self, question: str) -> dict[str, Any]:
        if not self.api_key:
            raise PlannerConfigurationError(
                "GROQ_API_KEY is required to answer questions."
            )

        if self.client is None:
            from groq import Groq

            self.client = Groq(api_key=self.api_key)

        try:
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
        except Exception as error:
            from groq import APIStatusError, NotFoundError, RateLimitError

            if isinstance(error, NotFoundError):
                raise PlannerModelError(
                    f"Groq model '{self.model}' is unavailable to this account. "
                    "Set GROQ_MODEL to an active model enabled for your account; "
                    "see https://console.groq.com/docs/models."
                ) from error
            if isinstance(error, RateLimitError) or (
                isinstance(error, APIStatusError) and error.status_code >= 500
            ):
                raise PlannerUnavailableError(
                    "Groq is temporarily unavailable or rate-limited. Please retry shortly."
                ) from error
            raise

        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Groq returned an empty query plan.")
        return validate_plan(json.loads(content))