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

    def test_scene_auto_advance_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "data"))
            svc = StoryrealmsService(store=store)
            svc.enter_realm("alpha", actor="test")
            svc.emit_event("flag.set", {"key": "scene_auto", "value": True}, actor="test")
            svc.emit_event("flag.set", {"key": "scene_period", "value": 2}, actor="test")

            svc.tick(1, actor="test")
            s1 = svc.query_state(realm="alpha")["state"]
            self.assertIsNone(s1.get("current_scene"))

            svc.tick(1, actor="test")
            s2 = svc.query_state(realm="alpha")["state"]
            self.assertEqual(s2.get("current_scene"), "scene:1")

    def test_npc_goal_planner_and_social_physics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "data"))
            svc = StoryrealmsService(store=store)
            svc.enter_realm("alpha", actor="test")
            svc.emit_event("entity.upsert", {"entity_id": "npc:1", "data": {"kind": "npc"}}, actor="test")
            svc.emit_event("entity.upsert", {"entity_id": "npc:2", "data": {"kind": "npc"}}, actor="test")
            svc.emit_event("npc.goal.set", {"entity_id": "npc:1", "goal": "socialize"}, actor="test")
            svc.tick(1, actor="test")

            state = svc.query_state(realm="alpha")["state"]
            rel = state.get("relationships") or {}
            # Social physics should have created/adjusted trust between npc:1 and npc:2.
            self.assertIn("npc:1", rel)
            self.assertIn("npc:2", rel.get("npc:1", {}))
            trust = rel["npc:1"]["npc:2"].get("trust")
            self.assertIsNotNone(trust)
            self.assertGreaterEqual(float(trust), 0.05)


if __name__ == "__main__":
    unittest.main()

