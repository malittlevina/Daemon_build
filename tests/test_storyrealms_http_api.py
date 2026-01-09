import os
import tempfile
import unittest

from storyrealms.http_api import route_request
from storyrealms.persistence import StoryrealmsStore
from storyrealms.service import StoryrealmsService


class TestStoryrealmsHttpApi(unittest.TestCase):
    def test_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svc = StoryrealmsService(store=StoryrealmsStore(base_dir=os.path.join(tmp, "data")))
            status, headers, body = route_request(svc, method="GET", path="/health", query={}, body=None)
            self.assertEqual(status, 200)
            self.assertEqual(body["status"], "ok")

    def test_view_and_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            svc = StoryrealmsService(store=StoryrealmsStore(base_dir=os.path.join(tmp, "data")))
            svc.enter_realm("alpha", actor="cli")
            status, _, _ = route_request(
                svc,
                method="POST",
                path="/realm/event",
                query={"realm": "alpha"},
                body={"type": "flag.set", "payload": {"key": "weather", "value": "rain"}, "actor": "cli"},
            )
            self.assertEqual(status, 200)
            status, _, view = route_request(svc, method="GET", path="/realm/view", query={"realm": "alpha", "limit": "10"}, body=None)
            self.assertEqual(status, 200)
            self.assertEqual(view["realm"], "alpha")
            self.assertEqual(view["view"]["flags"]["weather"], "rain")


if __name__ == "__main__":
    unittest.main()

