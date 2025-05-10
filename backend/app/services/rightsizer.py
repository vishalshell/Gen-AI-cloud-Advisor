"""Rightsizing engine that consults both GPT‑4o and Gemini 2 Pro and returns a consensus."""
import os, asyncio
from typing import Literal
from pydantic import BaseModel
from openai import AsyncOpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

v_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
v_gemini_model = genai.GenerativeModel("gemini-2-pro")  # switched to stable Pro

class InstanceMetrics(BaseModel):
    cpu: float  # average CPU util %
    mem: float  # average memory util %

    def to_prompt(self) -> str:
        return (f"Instance metrics: CPU average {self.cpu:.1f} %, "
                f"Memory average {self.mem:.1f} %. "
                "Provide a single rightsizing recommendation: "
                "`DOWNGRADE`, `KEEP`, or `UPGRADE`, "
                "followed by short reasoning in one sentence.")

class RightsizeResult(BaseModel):
    decision: Literal["DOWNGRADE", "KEEP", "UPGRADE"]
    reasoning: str

class Rightsizer:
    async def _ask_gpt(self, v_prompt: str) -> RightsizeResult:
        v_resp = await v_openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an AWS rightsizing expert."},
                      {"role": "user", "content": v_prompt}]
        )
        return self._parse(v_resp.choices[0].message.content)

    async def _ask_gemini(self, v_prompt: str) -> RightsizeResult:
        v_resp = await v_gemini_model.generate_content_async(v_prompt)
        return self._parse(v_resp.text)

    def _parse(self, v_text: str) -> RightsizeResult:
        v_text = v_text.strip()
        v_parts = v_text.split(None, 1)
        v_decision = v_parts[0].upper()
        if v_decision not in {"DOWNGRADE", "KEEP", "UPGRADE"}:
            v_decision = "KEEP"
        v_reason = v_parts[1].strip() if len(v_parts) > 1 else ""
        return RightsizeResult(decision=v_decision, reasoning=v_reason)

    async def suggest(self, v_instance_id: str, v_metrics: InstanceMetrics):
        v_prompt = v_metrics.to_prompt()
        v_gpt_task = asyncio.create_task(self._ask_gpt(v_prompt))
        v_gemini_task = asyncio.create_task(self._ask_gemini(v_prompt))
        gpt_res, gemini_res = await asyncio.gather(v_gpt_task, v_gemini_task)

        # Consensus logic
        if gpt_res.decision == gemini_res.decision:
            final_decision = gpt_res.decision
            reasoning = f"Both models agree: {gpt_res.reasoning}"
        else:
            final_decision = "KEEP"
            reasoning = (f"GPT‑4o suggests {gpt_res.decision} ({gpt_res.reasoning}); "
                         f"Gemini 2 Pro suggests {gemini_res.decision} ({gemini_res.reasoning}). "
                         "Defaulting to KEEP until further analysis.")
        return {
            "decision": final_decision,
            "reasoning": reasoning,
            "gpt_opinion": f"{gpt_res.decision}: {gpt_res.reasoning}",
            "gemini_opinion": f"{gemini_res.decision}: {gemini_res.reasoning}"
        }
