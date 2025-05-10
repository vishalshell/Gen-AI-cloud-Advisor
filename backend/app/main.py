from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.chat import chat_with_llm
from app.services.rightsizer import Rightsizer, InstanceMetrics

app = FastAPI(title="Gen‑AI Cloud Advisor (AWS)")

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    answer: str

class RightsizeRequest(BaseModel):
    instance_id: str
    avg_cpu: float
    avg_mem: float

class RightsizeResponse(BaseModel):
    decision: str
    reasoning: str
    gpt_opinion: str
    gemini_opinion: str

rightsizer = Rightsizer()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        v_answer = await chat_with_llm(req.prompt)
        return {"answer": v_answer}
    except Exception as v_exc:
        raise HTTPException(status_code=500, detail=str(v_exc))

@app.post("/rightsizing", response_model=RightsizeResponse)
async def rightsizing(req: RightsizeRequest):
    try:
        v_metrics = InstanceMetrics(cpu=req.avg_cpu, mem=req.avg_mem)
        v_out = await rightsizer.suggest(req.instance_id, v_metrics)
        return v_out
    except Exception as v_exc:
        raise HTTPException(status_code=500, detail=str(v_exc))
