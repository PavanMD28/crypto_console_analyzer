from typing import Dict, Any, Optional
from datetime import datetime
from config import configure_gemini

class MemoryLayer:
    def __init__(self):
        self.model = configure_gemini()
        self.memory_store = {}

    async def store(self, key: str, data: Dict[str, Any], context: str) -> None:
        self.memory_store[key] = {
            'data': data,
            'context': context,
            'timestamp': datetime.now()
        }

    async def retrieve(self, key: str, context: str) -> Optional[Dict[str, Any]]:
        return self.memory_store.get(key, {}).get('data', None)