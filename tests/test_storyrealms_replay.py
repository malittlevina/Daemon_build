import os
import tempfile
import unittest

from storyrealms.persistence import StoryrealmsStore
from storyrealms.service import StoryrealmsService


class TestStoryrealmsReplay(unittest.TestCase):
    def test_replay_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "storyrealms_data"))
            svc1 = StoryrealmsService(store=store)

            svc1.enter_realm("alpha", actor="test")
            svc1.emit_event("flag.set", {"key": "weather", "value": "rain"}, actor="test")
            svc1.emit_event("entity.upsert", {"entity_id": "npc:1", "data": {"name": "Ira", "mood": "curious"}}, actor="test")
            svc1.tick(3, actor="test")

            s1 = svc1.query_state(realm="alpha")["state"]

            # New service instance reading the same store should reconstruct the same state.
            svc2 = StoryrealmsService(store=store)
            svc2.replay(realm="alpha")
            s2 = svc2.query_state(realm="alpha")["state"]

            self.assertEqual(s1, s2)


if __name__ == "__main__":
    unittest.main()

