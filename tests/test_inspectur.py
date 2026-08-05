from pathlib import Path
import unittest

from click.testing import CliRunner

from inspectur.cli import cli


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class InspecturCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.global_args = ["--root", str(REPOSITORY_ROOT), "--no-color"]

    def test_help_lists_repository_commands(self) -> None:
        result = self.runner.invoke(cli, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("list", result.output)
        self.assertIn("matrix", result.output)
        self.assertIn("check", result.output)

    def test_default_command_displays_inventory(self) -> None:
        result = self.runner.invoke(cli, self.global_args)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Base images", result.output)
        self.assertIn("actions-runner", result.output)

    def test_show_displays_one_image(self) -> None:
        result = self.runner.invoke(cli, [*self.global_args, "show", "ubuntu", "24.04"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("ubuntu:24.04", result.output)
        self.assertIn("Published as", result.output)

    def test_check_fails_for_placeholder_digests(self) -> None:
        result = self.runner.invoke(cli, [*self.global_args, "check"])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Blocked image definitions", result.output)

    def test_runtime_matrix_is_discovered(self) -> None:
        result = self.runner.invoke(cli, [*self.global_args, "matrix", "--runtime", "node"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Node runtime matrix", result.output)
        self.assertIn("alpine", result.output)


if __name__ == "__main__":
    unittest.main()
