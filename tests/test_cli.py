from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cli import main


class CLITests(unittest.TestCase):
    def run_cli(self, *args: str) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(args)
        self.assertEqual(exit_code, 0)
        return buffer.getvalue()

    def test_sort_command_uses_adaptive_selector(self) -> None:
        output = self.run_cli("sort", "--data", "5,3,4,1")
        self.assertIn("Recommended:", output)
        self.assertIn("Sorted data: [1, 3, 4, 5]", output)

    def test_search_command_finds_target(self) -> None:
        output = self.run_cli(
            "search",
            "--data",
            "1,3,5,7,9",
            "--target",
            "7",
            "--assume-sorted",
        )
        self.assertIn("Target 7 found at index 3.", output)

    def test_benchmark_command_writes_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "benchmark.csv"
            dashboard_path = Path(tmpdir) / "results-data.js"
            output = self.run_cli(
                "benchmark",
                "--kind",
                "sorting",
                "--sizes",
                "10",
                "20",
                "--trials",
                "1",
                "--output",
                str(output_path),
                "--dashboard-output",
                str(dashboard_path),
            )
            self.assertIn("Benchmarked", output)
            self.assertTrue(output_path.exists())
            self.assertTrue(dashboard_path.exists())
