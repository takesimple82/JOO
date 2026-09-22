from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MINIMUM_SUITE_COUNT = 80
MINIMUM_TEST_COUNT = 1573
_RAN_PATTERN = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)


def active_test_suites() -> tuple[Path, ...]:
    suites = []
    for path in ROOT.rglob("tests"):
        if not path.is_dir():
            continue
        relative = path.relative_to(ROOT)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if any(path.glob("test_*.py")):
            suites.append(relative)
    return tuple(sorted(suites, key=lambda item: item.as_posix()))


def run_repository_tests() -> tuple[int, int]:
    suites = active_test_suites()
    if len(suites) < MINIMUM_SUITE_COUNT:
        raise AssertionError(
            "deterministic discovery found "
            f"{len(suites)} suites; expected at least "
            f"{MINIMUM_SUITE_COUNT}"
        )

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    total = 0
    failures = []
    for suite in suites:
        completed = subprocess.run(
            (
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                suite.as_posix(),
                "-p",
                "test_*.py",
                "-q",
            ),
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        output = completed.stdout + completed.stderr
        match = _RAN_PATTERN.search(output)
        if match is None:
            failures.append(
                f"{suite}: test count was not reported\n{output}"
            )
            continue
        count = int(match.group(1))
        if count == 0:
            failures.append(f"{suite}: collected zero tests")
            continue
        total += count
        if completed.returncode != 0:
            failures.append(f"{suite}:\n{output}")

    if total < MINIMUM_TEST_COUNT:
        failures.append(
            "deterministic discovery collected "
            f"{total} tests; expected at least {MINIMUM_TEST_COUNT}"
        )
    if failures:
        raise AssertionError("\n\n".join(failures))

    print(
        "Repository deterministic baseline: "
        f"{len(suites)} suites, {total} tests, "
        f"{total} passed, 0 failures/errors"
    )
    return len(suites), total


class RepositoryDeterministicBaselineTests(unittest.TestCase):
    def test_all_active_suites_are_collected_and_green(self):
        suite_count, test_count = run_repository_tests()
        self.assertGreaterEqual(suite_count, MINIMUM_SUITE_COUNT)
        self.assertGreaterEqual(test_count, MINIMUM_TEST_COUNT)


if __name__ == "__main__":
    try:
        run_repository_tests()
    except AssertionError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
