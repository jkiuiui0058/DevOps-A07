"""B-role checks for declared edges and the MD/RD evidence contract.

These use small, independent syscall transcripts rather than saved E6 output,
so a regression in parsing or set subtraction cannot be hidden by stale files.
"""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import analyze


class TestE6BDeclaredDifferenceEvidence(unittest.TestCase):
    def test_difference_preserves_actual_and_declaration_anchors(self):
        """MD has read/write anchors; RD keeps its Make-database anchor."""
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            root = "/course/project"
            (folder / "t.10").write_text(
                'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 11\n',
                encoding="utf-8",
            )
            (folder / "t.11").write_text(
                'execve("/usr/bin/cc", ["cc", "-c", "unit.c"], []) = 0\n'
                'openat(AT_FDCWD, "unit.c", O_RDONLY) = 3\n'
                'openat(AT_FDCWD, "needed.h", O_RDONLY) = 4\n'
                'openat(AT_FDCWD, "unit.o", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 5\n',
                encoding="utf-8",
            )
            database = folder / "make-db.txt"
            database.write_text(
                "# Files\nunit.o: unit.c extra.h\n# files hash-table stats:\n",
                encoding="utf-8",
            )

            result = analyze(folder, database, root)

        findings = {(item["type"], item["dependency"]): item for item in result["findings"]}
        missing = findings[("MISSING", "needed.h")]
        redundant = findings[("REDUNDANT", "extra.h")]
        self.assertEqual(missing["target"], "unit.o")
        self.assertEqual(missing["declared_dependencies"], ["extra.h", "unit.c"])
        self.assertEqual(
            [(anchor["source"], anchor["trace_file"], anchor["line"]) for anchor in missing["evidence"]],
            [("system_call", "t.11", 3), ("system_call", "t.11", 4)],
        )
        self.assertEqual(redundant["evidence"][0]["source"], "make_database")
        self.assertEqual(redundant["evidence"][0]["artifact"], "make-db.txt")
        self.assertEqual(redundant["evidence"][0]["line"], 2)
        self.assertEqual(redundant["evidence"][0]["declaration"], "unit.o: unit.c extra.h")


if __name__ == "__main__":
    unittest.main()
