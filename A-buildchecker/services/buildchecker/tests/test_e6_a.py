"""Independent synthetic traces check isolation between two recipe jobs."""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import execution_graph


class TestE6A(unittest.TestCase):
    def test_two_recipe_jobs_keep_inputs_processes_and_evidence_separate(self):
        # All PIDs and syscall lines below are synthetic, not collected evidence.
        traces = {
            10: 'execve("/usr/bin/make", ["make", "a.o", "b.o"], []) = 0\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 11\n'
                'clone(child_stack=NULL, flags=SIGCHLD) = 21\n',
        }
        for name, job, reader, writer in (("a", 11, 12, 13), ("b", 21, 22, 23)):
            traces[job] = (
                f'execve("/usr/bin/cc", ["cc", "-c", "{name}.c", "-o", "{name}.o"], []) = 0\n'
                f'clone(child_stack=NULL, flags=SIGCHLD) = {reader}\n'
                f'clone(child_stack=NULL, flags=SIGCHLD) = {writer}\n'
            )
            traces[reader] = (
                f'execve("/usr/bin/cc1", ["cc1", "{name}.c"], []) = 0\n'
                f'openat(AT_FDCWD, "{name}.c", O_RDONLY) = 3\n'
                f'openat(AT_FDCWD, "{name}.h", O_RDONLY) = 4\n'
            )
            traces[writer] = (
                f'execve("/usr/bin/as", ["as", "-o", "{name}.o"], []) = 0\n'
                f'openat(AT_FDCWD, "{name}.o", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3\n'
            )

        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for pid, text in traces.items():
                (folder / f"t.{pid}").write_text(text, encoding="utf-8")
            targets, processes = execution_graph(folder, "/course/project")

        self.assertEqual(set(targets), {"a.o", "b.o"})
        for name, job, reader, writer in (("a", 11, 12, 13), ("b", 21, 22, 23)):
            with self.subTest(target=f"{name}.o"):
                target = targets[f"{name}.o"]
                self.assertEqual(set(target["dependencies"]), {f"{name}.c", f"{name}.h"})
                self.assertEqual(target["job_pid"], job)
                self.assertEqual(target["processes"], [job, reader, writer])
                self.assertEqual(
                    {(dep, ev["pid"], ev["trace_file"], ev["line"])
                     for dep, ev in target["dependencies"].items()},
                    {(f"{name}.c", reader, f"t.{reader}", 2),
                     (f"{name}.h", reader, f"t.{reader}", 3)},
                )
                self.assertEqual(target["output_evidence"], {
                    "source": "system_call", "trace_file": f"t.{writer}",
                    "line": 2, "pid": writer, "operation": "openat",
                })
        self.assertEqual(
            {(p["pid"], p["parent"], p["job_pid"]) for p in processes},
            {(10, None, None), (11, 10, 11), (12, 11, 11), (13, 11, 11),
             (21, 10, 21), (22, 21, 21), (23, 21, 21)},
        )


if __name__ == "__main__":
    unittest.main()
