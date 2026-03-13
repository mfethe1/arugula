import asyncio
import json

async def mock_nats_publish(subject, payload):
    """Simulates publishing a message to NATS."""
    print(f"[NATS] Published to {subject}: {json.dumps(payload)}")
    await asyncio.sleep(0.1)

async def mock_nats_subscribe(subject, callback):
    """Simulates subscribing to a NATS subject."""
    print(f"[NATS] Subscribed to {subject}")
    # In a real system, this would listen and await messages.
    pass
