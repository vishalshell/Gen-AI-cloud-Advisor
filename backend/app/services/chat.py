import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from qdrant_client import QdrantClient

load_dotenv()

v_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
v_qdrant = QdrantClient(
    host=os.getenv('VECTOR_DB_HOST', 'localhost'),
    port=int(os.getenv('VECTOR_DB_PORT', 6333))
)

async def chat_with_llm(v_prompt: str) -> str:
    """Thin wrapper around the selected LLM.

    TODO: add retrieval-augmented generation using v_qdrant.
    """
    v_resp = await v_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a FinOps assistant for AWS."},
            {"role": "user", "content": v_prompt}
        ]
    )
    return v_resp.choices[0].message.content
