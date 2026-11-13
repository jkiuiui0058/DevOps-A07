"""Independent synthetic traces check ambiguous target ownership."""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import Unsupported, execution_graph


class TestE7A(unittest.TestCase):
    def test_two_recipe_jobs_writing_same_target_fail_instead_of_merging(self):
        # All PIDs and syscall lines below are synthetic, not collected evidence.
        traces = {
            10: 'execve("/usr/bin/make", ["make", "app"], []) = 0\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 11\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 21\n',
        }
        for name, job in (("a", 11), ("b", 21)):
            traces[job] = (
                f'execve("/usr/bin/cc", ["cc", "-c", "{name}.c", "-o", "shared.o"], []) = 0\n'
                f'openat(AT_FDCWD, "{name}.c", O_RDONLY) = 3\n'
                'openat(AT_FDCWD, "shared.o", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 4\n'
            )

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for pid, text in traces.items():
                (folder / f"t.{pid}").write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(Unsupported, r"^Multiple jobs write the same target: shared\.o$"):
                execution_graph(folder, "/course/project")


if __name__ == "__main__":
    unittest.main()
