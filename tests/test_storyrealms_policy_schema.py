import os
import tempfile
import unittest

from storyrealms.events import RealmEvent
from storyrealms.persistence import StoryrealmsStore
from storyrealms.service import StoryrealmsService


class TestPolicyAndSchema(unittest.TestCase):
    def test_unknown_actor_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "data"))
            svc = StoryrealmsService(store=store)
            svc.policy.strict = True
            svc.enter_realm("alpha", actor="cli")
            with self.assertRaises(PermissionError):
                svc.emit_event("flag.set", {"key": "x", "value": 1}, actor="someone_else")

    def test_schema_rejects_bad_flag_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = StoryrealmsStore(base_dir=os.path.join(tmp, "data"))
            svc = StoryrealmsService(store=store)
            svc.enter_realm("alpha", actor="cli")
            with self.assertRaises(Exception):
                svc.emit_event("flag.set", {"value": 1}, actor="cli")  # missing key


if __name__ == "__main__":
    unittest.main()

