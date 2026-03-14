import asyncio
import base64
import json
import os

# Try to import NATS client, fall back to mock if not available
try:
    import nats

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

# NATS configuration from environment or defaults
NATS_URL = os.environ.get("NATS_URL", "nats://gondola.proxy.rlwy.net:22393")


class NATSClient:
    """Real NATS client with automatic fallback to mock."""

    def __init__(self):
        self.client = None
        self.connected = False
        self._connect_task = None

    async def connect(self):
        """Connect to NATS server."""
        if not NATS_AVAILABLE:
            print("[NATS] nats-py not installed, using mock client")
            return False

        try:
            self.client = await nats.connect(NATS_URL)
            self.connected = True
            print(f"[NATS] Connected to {NATS_URL}")
            return True
        except Exception as e:
            print(f"[NATS] Connection failed: {e}, using mock client")
            self.connected = False
            return False

    async def publish(self, subject, payload):
        """Publish message to NATS subject."""
        if self.connected and self.client:
            try:
                await self.client.publish(subject, json.dumps(payload).encode())
                print(f"[NATS] Published to {subject}: {json.dumps(payload)}")
                return True
            except Exception as e:
                print(f"[NATS] Publish failed: {e}")
        # Fall back to mock
        await mock_nats_publish(subject, payload)
        return False

    async def subscribe(self, subject, callback):
        """Subscribe to NATS subject."""
        if self.connected and self.client:
            try:
                await self.client.subscribe(subject, cb=callback)
                print(f"[NATS] Subscribed to {subject}")
                return True
            except Exception as e:
                print(f"[NATS] Subscribe failed: {e}")
        # Fall back to mock
        await mock_nats_subscribe(subject, callback)
        return False

    async def close(self):
        """Close NATS connection."""
        if self.client and self.connected:
            await self.client.close()
            self.connected = False


# Global client instance
_nats_client = None


async def get_nats_client():
    """Get or create NATS client."""
    global _nats_client
    if _nats_client is None:
        _nats_client = NATSClient()
        await _nats_client.connect()
    return _nats_client


async def nats_publish(subject, payload):
    """
    Primary NATS publish function.
    Uses real NATS if available, falls back to mock.
    """
    client = await get_nats_client()
    return await client.publish(subject, payload)


async def nats_subscribe(subject, callback):
    """Subscribe to NATS subject."""
    client = await get_nats_client()
    return await client.subscribe(subject, callback)


# Keep backward compatibility
async def mock_nats_publish(subject, payload):
    """Simulates publishing a message to NATS (fallback)."""
    print(f"[NATS] Published to {subject}: {json.dumps(payload)}")
    await asyncio.sleep(0.1)


async def mock_nats_subscribe(subject, callback):
    """Simulates subscribing to a NATS subject (fallback)."""
    print(f"[NATS] Subscribed to {subject}")
    # In a real system, this would listen and await messages.
    pass
