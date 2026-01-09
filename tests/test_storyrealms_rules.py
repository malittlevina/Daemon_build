import os
import tempfile
import unittest

from storyrealms.persistence import StoryrealmsStore
from storyrealms.service import StoryrealmsService


class TestStoryrealmsRules(unittest.TestCase):
    def test_tick_derives_npc_mood_from_weather(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "data"))
            svc = StoryrealmsService(store=store)
            svc.enter_realm("alpha", actor="test")
            svc.emit_event("flag.set", {"key": "weather", "value": "rain"}, actor="test")
            svc.emit_event("entity.upsert", {"entity_id": "npc:1", "data": {"kind": "npc", "mood": "neutral"}}, actor="test")
            svc.tick(1, actor="test")

            state = svc.query_state(realm="alpha")["state"]
            self.assertEqual(state["entities"]["npc:1"]["mood"], "pensive")


if __name__ == "__main__":
    unittest.main()

