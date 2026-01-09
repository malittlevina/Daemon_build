import unittest

from storyrealms.commands import parse_storyrealms_command


class TestStoryrealmsCommands(unittest.TestCase):
    def test_entity_show(self) -> None:
        cmd = parse_storyrealms_command("entity show npc:1")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.name, "entity.show")
        self.assertEqual(cmd.args["entity_id"], "npc:1")

    def test_npc_list(self) -> None:
        cmd = parse_storyrealms_command("npc list")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.name, "npc.list")

    def test_npc_goal_add(self) -> None:
        cmd = parse_storyrealms_command("npc goal add npc:1 socialize")
        self.assertIsNotNone(cmd)
        assert cmd is not None
        self.assertEqual(cmd.name, "npc.goal.set")
        self.assertEqual(cmd.args["entity_id"], "npc:1")
        self.assertEqual(cmd.args["goal"], "socialize")


if __name__ == "__main__":
    unittest.main()

