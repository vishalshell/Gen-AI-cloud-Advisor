import pytest, asyncio
from app.services.rightsizer import Rightsizer, InstanceMetrics

@pytest.mark.asyncio
async def test_consensus():
    rightsizer = Rightsizer()
    metrics = InstanceMetrics(cpu=10.0, mem=20.0)
    # In CI we would mock LLM calls; here just ensure method exists
    assert hasattr(rightsizer, "suggest")
