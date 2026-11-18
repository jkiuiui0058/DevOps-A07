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
class StudentE8A_241250005(unittest.TestCase):
    def test_declaration_change_reuses_actual_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            f=p/'Makefile'
            f.write_text(f.read_text().replace('main.c unused.h','main.c unused.h config.h'))
            commit(p,'student: add missing declaration')
            result=scan(p,old)
            self.assertEqual(result['actual'],old['actual'])
            self.assertEqual(set(result['reused']),{'main.o','helper.o'})
            self.assertEqual(result['refreshed'],[])
            self.assertEqual(
                {(x['type'],x['target'],x['dependency']) for x in result['findings']},
                {('REDUNDANT','main.o','unused.h')})

class StudentE8AIndirectInclude_241250005(unittest.TestCase):
    def test_indirect_include_invalidates_old_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            (p/'config.h').write_text('#include "extra.h"\n#define VALUE 1\n')
            commit(p,'student: indirect include inside config.h')
            r=scan(p,old)
            self.assertEqual(r['actual']['main.o'],['config.h','extra.h','main.c'])
            self.assertIn(['MISSING','main.o','extra.h'],r['added'])
            self.assertEqual(r['refreshed'],['main.o','helper.o'])
            self.assertEqual(r['reused'],[])

class StudentE9AExtra_241250005(unittest.TestCase):
    def test_flags_change_refreshes_all_but_findings_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            f=p/'Makefile'
            f.write_text(f.read_text().replace('CFLAGS = -O0','CFLAGS = -O1'))
            commit(p,'student: switch optimization flags')
            r=scan(p,old)
            self.assertEqual(r['refreshed'],['main.o','helper.o'])
            self.assertEqual(r['reused'],[])
            self.assertEqual(r['actual'],old['actual'])
            self.assertEqual(r['findings'],old['findings'])
            self.assertEqual(r['added'],[])
            self.assertEqual(r['resolved'],[])

    def test_revert_restores_reuse_from_old_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'sample'
            fixture(p)
            old=scan(p)
            f=p/'main.c'
            added='#include "extra.h"\n'+f.read_text()
            f.write_text(added);commit(p,'student: temporary include')
            f.write_text(f.read_text().replace('#include "extra.h"\n',''));commit(p,'student: revert include')
            r=scan(p,old)
            self.assertEqual(r['reused'],['main.o','helper.o'])
            self.assertEqual(r['refreshed'],[])
            self.assertEqual(r['findings'],old['findings'])
            self.assertEqual(r['added'],[])
            self.assertEqual(r['resolved'],[])

if __name__=='__main__':unittest.main()
