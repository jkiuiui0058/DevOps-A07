import json, tempfile, unittest
from pathlib import Path
from lab import fixture,scan,patch,commit

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'sample';fixture(self.p)

    def test_independent_known_edges(self):
        r=scan(self.p)
        self.assertEqual(r['actual']['main.o'],['config.h','main.c'])
        self.assertEqual({(f['type'],f['dependency']) for f in r['findings']},{('MISSING','config.h'),('REDUNDANT','unused.h')})

    def test_unchanged_reuses_both_targets(self):
        r=scan(self.p,scan(self.p));self.assertEqual(r['reused'],['main.o','helper.o']);self.assertEqual(r['refreshed'],[])

    def test_include_added_invalidates_cache(self):
        old=scan(self.p)
        (self.p/'main.c').write_text('#include "extra.h"\n'+(self.p/'main.c').read_text());commit(self.p,'new include')
        r=scan(self.p,old)
        self.assertIn(['MISSING','main.o','extra.h'],r['added']);self.assertEqual(len(r['refreshed']),2)

    def test_patch_preserves_redundant_dependency(self):
        r=scan(self.p);diff,plan=patch(self.p,r)
        self.assertIn('+main.o: main.c unused.h config.h',diff)
        self.assertNotIn('-\tgcc',diff)
        self.assertNotIn('config.h',(self.p/'Makefile').read_text())

    def test_old_report_rejected(self):
        r=scan(self.p);r['commit']='0'*40
        with self.assertRaisesRegex(ValueError,'STALE_REPORT'):patch(self.p,r)

    def test_unsafe_dependency_rejected(self):
        r=scan(self.p);r['findings']=[{'type':'MISSING','target':'main.o','dependency':'../outside.h'}]
        with self.assertRaisesRegex(ValueError,'UNSAFE_PATH'):patch(self.p,r)

    def test_unsupported_configuration_rejected(self):
        (self.p/'Makefile').write_text((self.p/'Makefile').read_text().replace('-O0','-include unknown.h'))
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_FLAGS'):scan(self.p)

class E8_newtest1(unittest.TestCase):
    def test_indirect_include_invalidates_history(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p)
            old = scan(p)

            # main.c不变，只改变它包含的头文件。
            header = p / 'config.h'
            header.write_text('#include "extra.h"\n#define VALUE 1\n')
            commit(p, 'student: add indirect header dependency')

            result = scan(p, old)
            self.assertEqual(
                result['actual']['main.o'],
                ['config.h', 'extra.h', 'main.c']
            )
            self.assertIn(
                ['MISSING', 'main.o', 'extra.h'], result['added']
            )
            self.assertEqual(result['reused'], [])
            self.assertEqual(
                set(result['refreshed']), {'main.o', 'helper.o'}
            )

            full = scan(p)
            self.assertEqual(result['actual'], full['actual'])
            self.assertEqual(result['findings'], full['findings'])

class E9_newtest1(unittest.TestCase):
    def test_removed_indirect_include_clears_old_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p)

            header = p / 'config.h'
            header.write_text('#include "extra.h"\n#define VALUE 1\n')
            commit(p, 'student: establish indirect include')
            old = scan(p)
            self.assertEqual(
                old['actual']['main.o'],
                ['config.h', 'extra.h', 'main.c']
            )

            # extra.h仍存在，只删除config.h中的包含指令。
            header.write_text('#define VALUE 1\n')
            commit(p, 'student: remove indirect include')
            result = scan(p, old)

            self.assertEqual(
                result['actual']['main.o'], ['config.h', 'main.c']
            )
            self.assertEqual(result['resolved'], [
                ['MISSING', 'main.o', 'extra.h']
            ])
            self.assertEqual(result['added'], [])
            self.assertEqual(result['reused'], [])
            self.assertEqual(
                set(result['refreshed']), {'main.o', 'helper.o'}
            )

            full = scan(p)
            self.assertEqual(result['actual'], full['actual'])
            self.assertEqual(result['findings'], full['findings'])
class StudentE8A_241098114(unittest.TestCase):
    def test_shared_header_include_refreshes_both_consumers(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p)
            (p/'helper.c').write_text('#include "config.h"\nint helper(void){return 0;}\n')
            commit(p, '241098114: prepare shared header consumers')
            old = scan(p)

            # Independent expected edges: both consumers already include config.h.
            self.assertEqual(old['actual'], {
                'main.o': ['config.h', 'main.c'],
                'helper.o': ['config.h', 'helper.c'],
            })
            old_findings = {
                ('MISSING', 'main.o', 'config.h'),
                ('REDUNDANT', 'main.o', 'unused.h'),
                ('MISSING', 'helper.o', 'config.h'),
            }
            self.assertEqual({(f['type'], f['target'], f['dependency'])
                              for f in old['findings']}, old_findings)

            # Only the shared header changes; both consumers gain extra.h.
            (p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
            commit(p, '241098114: extend shared header include')
            result = scan(p, old)
            full = scan(p)
            self.assertEqual(result['actual'], {
                'main.o': ['config.h', 'extra.h', 'main.c'],
                'helper.o': ['config.h', 'extra.h', 'helper.c'],
            })
            self.assertEqual({(f['type'], f['target'], f['dependency'])
                              for f in result['findings']}, old_findings | {
                ('MISSING', 'main.o', 'extra.h'),
                ('MISSING', 'helper.o', 'extra.h'),
            })
            self.assertEqual(result['added'], [
                ['MISSING', 'helper.o', 'extra.h'],
                ['MISSING', 'main.o', 'extra.h'],
            ])
            self.assertEqual(result['resolved'], [])
            self.assertEqual(result['reused'], [])
            self.assertEqual(result['refreshed'], ['main.o', 'helper.o'])
            self.assertEqual(result['declared'], old['declared'])
            self.assertNotEqual(result['key'], old['key'])
            for field in ['actual', 'declared', 'findings']:
                self.assertEqual(result[field], full[field], field)


class StudentE9A_241098114(unittest.TestCase):
    def test_enabling_conditional_include_resolves_redundant_edge(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample'
            fixture(p)
            header = p/'config.h'
            header.write_text('#if 0\n#include "extra.h"\n#endif\n#define VALUE 1\n')
            makefile = p/'Makefile'
            makefile.write_text(makefile.read_text().replace(
                'main.o: main.c unused.h', 'main.o: main.c unused.h extra.h'))
            commit(p, '241098114: prepare disabled conditional include')
            old = scan(p)

            # A disabled include is not an actual edge, despite its declaration.
            self.assertEqual(old['actual'], {
                'main.o': ['config.h', 'main.c'],
                'helper.o': ['helper.c'],
            })
            self.assertEqual({(f['type'], f['target'], f['dependency'])
                              for f in old['findings']}, {
                ('MISSING', 'main.o', 'config.h'),
                ('REDUNDANT', 'main.o', 'extra.h'),
                ('REDUNDANT', 'main.o', 'unused.h'),
            })

            # Toggle only the condition: the declared extra.h edge becomes real.
            header.write_text(header.read_text().replace('#if 0', '#if 1'))
            commit(p, '241098114: enable conditional include')
            result = scan(p, old)
            full = scan(p)
            self.assertEqual(result['actual'], {
                'main.o': ['config.h', 'extra.h', 'main.c'],
                'helper.o': ['helper.c'],
            })
            self.assertEqual({(f['type'], f['target'], f['dependency'])
                              for f in result['findings']}, {
                ('MISSING', 'main.o', 'config.h'),
                ('REDUNDANT', 'main.o', 'unused.h'),
            })
            self.assertEqual(result['added'], [])
            self.assertEqual(result['resolved'], [['REDUNDANT', 'main.o', 'extra.h']])
            self.assertEqual(result['reused'], [])
            self.assertEqual(result['refreshed'], ['main.o', 'helper.o'])
            self.assertEqual(result['declared'], old['declared'])
            self.assertNotEqual(result['key'], old['key'])
            for field in ['actual', 'declared', 'findings']:
                self.assertEqual(result[field], full[field], field)


if __name__=='__main__':unittest.main()
