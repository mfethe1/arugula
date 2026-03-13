import asyncio
from core.evaluator import FitnessEvaluator
from core.nats_client import mock_nats_publish
import random

def buildbid_fitness(prompt_text):
    """Mock fitness function for BuildBid vision extraction."""
    # Simulates precision/recall of extracted line items
    base_score = 0.85
    noise = random.uniform(-0.05, 0.08)
    return min(1.0, base_score + noise)

def trading_fitness(prompt_text):
    """Mock fitness function for Trading Agent Sharpe ratio."""
    # Simulates rolling Sharpe ratio
    base_score = 1.2
    noise = random.uniform(-0.3, 0.5)
    return base_score + noise

def memu_fitness(prompt_text):
    """Mock fitness function for memU retrieval accuracy."""
    # Simulates memory utilization rate
    base_score = 0.70
    noise = random.uniform(-0.1, 0.15)
    return min(1.0, base_score + noise)

async def run_arugula():
    print("Starting ARUGULA (Autoresearch Universal General Utility Learning Architecture)...")
    await mock_nats_publish("arugula.system.status", {"status": "starting", "projects": ["buildbid", "trading", "memu"]})

    # Setup prompt files
    for proj in ["buildbid", "trading", "memu"]:
        with open(f"{proj}_prompt.txt", 'w') as f:
            f.write(f"Initial prompt for {proj}")

    eval_bb = FitnessEvaluator("BuildBid", buildbid_fitness)
    eval_tr = FitnessEvaluator("Trading", trading_fitness)
    eval_mu = FitnessEvaluator("memU", memu_fitness)

    await mock_nats_publish("arugula.buildbid.status", {"status": "evaluating"})
    eval_bb.evolve("buildbid_prompt.txt", iterations=3)

    await mock_nats_publish("arugula.trading.status", {"status": "evaluating"})
    eval_tr.evolve("trading_prompt.txt", iterations=3)

    await mock_nats_publish("arugula.memu.status", {"status": "evaluating"})
    eval_mu.evolve("memu_prompt.txt", iterations=3)

    print("ARUGULA autoresearch loops completed.")
    await mock_nats_publish("arugula.system.status", {"status": "completed"})

if __name__ == "__main__":
    asyncio.run(run_arugula())
