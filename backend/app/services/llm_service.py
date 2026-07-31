"""
Pluggable LLM layer used for:
  1. Plain-language diagnosis explanations
  2. The farm chatbot
  3. The sell/hold advisor agent (function/tool calling)
  4. Translation into vernacular languages

Supports OpenAI, Anthropic, and Groq (OpenAI-compatible) natively. If no API key is configured,
falls back to a rule-based "mock LLM" so the whole app still runs and
demos end-to-end without any keys - real language generation kicks in
the moment a key is added to .env.
"""
from __future__ import annotations
import json
import logging
from typing import List, Dict, Any, Optional, Callable

from app.config import settings

logger = logging.getLogger("agrisense.llm")


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self._client = None
        self._model = None

        if self.provider == "openai" and settings.OPENAI_API_KEY:
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = settings.OPENAI_MODEL
        elif self.provider == "groq" and settings.GROQ_API_KEY:
            # Groq exposes an OpenAI-compatible /chat/completions API, so we
            # reuse the `openai` SDK and just point it at Groq's base URL -
            # no extra dependency needed, and it reuses all the OpenAI code
            # paths below (including tool/function calling).
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
            self._model = settings.GROQ_MODEL
        elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            import anthropic
            self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self._model = settings.ANTHROPIC_MODEL
        else:
            logger.warning(
                f"No API key found for provider '{self.provider}'. "
                "LLMService running in MOCK mode - responses are rule-based, not real LLM output."
            )
            self.provider = "mock"

        # Both "openai" and "groq" speak the OpenAI chat-completions schema,
        # so the existing OpenAI code paths handle both.
        self._uses_openai_schema = self.provider in ("openai", "groq")

    # ------------------------------------------------------------------ #
    # Plain chat (no tools) - used for diagnosis explanation & chatbot
    # ------------------------------------------------------------------ #
    def chat(self, system_prompt: str, user_message: str, history: Optional[List[Dict]] = None) -> str:
        history = history or []

        if self._uses_openai_schema:
            messages = [{"role": "system", "content": system_prompt}]
            messages += history
            messages.append({"role": "user", "content": user_message})
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.4,
            )
            return resp.choices[0].message.content

        if self.provider == "anthropic":
            resp = self._client.messages.create(
                model=self._model,
                max_tokens=800,
                system=system_prompt,
                messages=(history + [{"role": "user", "content": user_message}]) or
                         [{"role": "user", "content": user_message}],
            )
            return "".join(block.text for block in resp.content if block.type == "text")

        return self._mock_chat(system_prompt, user_message)

    def _mock_chat(self, system_prompt: str, user_message: str) -> str:
        return (
            "[Demo mode - no LLM API key set] Based on what you've told me, here's a simple "
            "summary: " + user_message[:220] +
            "\n\nAdd an OPENAI_API_KEY or ANTHROPIC_API_KEY to backend/.env to get real, "
            "detailed AI explanations here."
        )

    # ------------------------------------------------------------------ #
    # Agentic tool-calling loop - used by the Sell/Hold advisor
    # ------------------------------------------------------------------ #
    def run_agent(
        self,
        system_prompt: str,
        user_message: str,
        tools: List[Dict[str, Any]],
        tool_impls: Dict[str, Callable[..., Any]],
        max_turns: int = 4,
    ) -> Dict[str, Any]:
        """
        Runs a tool-calling loop until the model stops requesting tools.
        `tools` must be provided in OpenAI function-calling schema; this
        method translates the schema for Anthropic automatically.
        Returns {"final_text": str, "tool_calls": [ {name, args, result}, ... ]}
        """
        if self._uses_openai_schema:
            return self._run_agent_openai(system_prompt, user_message, tools, tool_impls, max_turns)
        if self.provider == "anthropic":
            return self._run_agent_anthropic(system_prompt, user_message, tools, tool_impls, max_turns)
        return self._run_agent_mock(system_prompt, user_message, tools, tool_impls)

    def _run_agent_openai(self, system_prompt, user_message, tools, tool_impls, max_turns):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        oai_tools = [{"type": "function", "function": t} for t in tools]
        trace = []

        for _ in range(max_turns):
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=oai_tools,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                return {"final_text": msg.content, "tool_calls": trace}

            messages.append(msg.model_dump(exclude_unset=True))
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                result = tool_impls[tc.function.name](**args)
                trace.append({"name": tc.function.name, "args": args, "result": result})
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })
        return {"final_text": "I gathered the data but ran out of turns to summarize it.", "tool_calls": trace}

    def _run_agent_anthropic(self, system_prompt, user_message, tools, tool_impls, max_turns):
        anthropic_tools = [
            {
                "name": t["name"],
                "description": t.get("description", ""),
                "input_schema": t.get("parameters", {"type": "object", "properties": {}}),
            }
            for t in tools
        ]
        messages = [{"role": "user", "content": user_message}]
        trace = []

        for _ in range(max_turns):
            resp = self._client.messages.create(
                model=self._model,
                max_tokens=1000,
                system=system_prompt,
                tools=anthropic_tools,
                messages=messages,
            )
            if resp.stop_reason != "tool_use":
                text = "".join(b.text for b in resp.content if b.type == "text")
                return {"final_text": text, "tool_calls": trace}

            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    result = tool_impls[block.name](**block.input)
                    trace.append({"name": block.name, "args": block.input, "result": result})
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    })
            messages.append({"role": "user", "content": tool_results})
        return {"final_text": "I gathered the data but ran out of turns to summarize it.", "tool_calls": trace}

    def _run_agent_mock(self, system_prompt, user_message, tools, tool_impls):
        """Deterministically calls every available tool once, then writes a
        simple rule-based recommendation from the combined results - keeps
        the advisor fully functional with zero API keys configured."""
        trace = []
        results = {}
        for t in tools:
            name = t["name"]
            try:
                result = tool_impls[name]()
            except TypeError:
                result = tool_impls[name](**{})
            trace.append({"name": name, "args": {}, "result": result})
            results[name] = result

        price_trend = results.get("get_price_trend", {})
        weather = results.get("get_weather_forecast", {})
        perishability = results.get("get_perishability", {})

        slope = price_trend.get("trend_slope_per_day", 0)
        rain_soon = weather.get("rain_expected_within_days") if weather else None
        shelf_life = perishability.get("shelf_life_days", 5) if perishability else 5

        if slope > 0 and (rain_soon is None or rain_soon > shelf_life):
            decision = "HOLD"
            reason = (f"[Demo mode] Prices are trending up (+{slope:.2f}/day) and no immediate "
                      f"spoilage risk given a shelf life of ~{shelf_life} days - holding a few more "
                      f"days looks favorable.")
        elif shelf_life <= 2 or (rain_soon is not None and rain_soon <= 1):
            decision = "SELL NOW"
            reason = (f"[Demo mode] The crop is highly perishable (~{shelf_life} days shelf life) "
                      f"or bad weather is imminent, so selling now avoids losses.")
        else:
            decision = "SELL NOW" if slope <= 0 else "HOLD"
            reason = f"[Demo mode] Based on a price slope of {slope:.2f}/day and {shelf_life}-day shelf life."

        return {
            "final_text": f"Recommendation: {decision}. {reason} "
                          f"(Add an OPENAI_API_KEY or ANTHROPIC_API_KEY to backend/.env for a "
                          f"real reasoning-based explanation here.)",
            "tool_calls": trace,
        }


llm_service = LLMService()
