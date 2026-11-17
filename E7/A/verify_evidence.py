"""Verify the delivered evidence offline, without extraction or dependencies."""
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

folder = Path(__file__).resolve().parent / 'evidence'
digest, name = (folder / 'PACKAGE.sha256').read_text().split()
data = (folder / name).read_bytes()
assert hashlib.sha256(data).hexdigest() == digest, 'package hash mismatch'


def members(blob):
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        entries = archive.getmembers()
        assert all(not p.issym() and not p.islnk() and not p.name.startswith('/')
                   and '..' not in PurePosixPath(p.name).parts for p in entries)
        files = [p for p in entries if p.isfile()]
        assert len({p.name for p in files}) == len(files), 'duplicate member'
        return {p.name: archive.extractfile(p).read() for p in files}


files = members(data)
manifest = json.loads(files['SHA256SUMS.json'])
assert set(files) == set(manifest) | {'SHA256SUMS.json'}
for path, expected in manifest.items():
    assert hashlib.sha256(files[path]).hexdigest() == expected, path

# Scan both the outer evidence and nested committed source; no extraction needed.
scanned = 0
patterns = [r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b',
            r'(?m)^-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----\r?$',
            r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            r'(?i)\b(?:ssh|scp)\s+-[A-Za-z]',
            r'(?i)\b(?:ssh|scp)\s+[\w.-]+@[\w.-]+']
pending = list(files.items())
while pending:
    path, blob = pending.pop()
    parts = PurePosixPath(path).parts
    assert not any(p in ('.ssh', '.aws', '.azure', '.git', 'credentials',
        'authorized_keys', 'known_hosts', 'id_rsa', 'id_ed25519', '.env',
        '.git-credentials', '.netrc', '.npmrc', '.pypirc') for p in parts), path
    assert not path.endswith(('.pem', '.key', '.p12', '.pfx', '.docker/config.json')), path
    if path.endswith(('.tar', '.tar.gz', '.tgz')):
        pending.extend((path + '!/' + p, b) for p, b in members(blob).items())
        continue
    scanned += 1
    text = blob.decode('utf-8', errors='replace')
    assert not any(re.search(pattern, text) for pattern in patterns), path


def load(path):
    return json.loads(files['evidence/' + path])


source_sha = 'e779b3130cd9b91eba4c6e54f4a6a85f5606b99c'
assert files['SOURCE_SHA'].decode().strip() == source_sha
assert load('provenance.json')['source_sha'] == source_sha
assert hashlib.sha256(files['source.tar']).hexdigest() == load('provenance.json')['source_archive_sha256']
assert load('image-inspect/stdout.log')[0]['Id'] == 'sha256:9cf27a2cd2c894be2d913717aed1e441a06013ea49e4a04c2fe87db4c3c8ab03'
for step in ('build', 'a01', 'service-tests', 'independent-six', 'full-gate'):
    assert load(step + '/exit.json')['exit_code'] == 0, step
assert b'21 passed' in files['evidence/service-tests/stdout.log']
assert b'Ran 6 tests' in files['evidence/independent-six/stderr.log']
gate = load('gate/gate-result.json')
rows = list(csv.DictReader(io.StringIO(files['evidence/gate/results.csv'].decode())))
expected_names = ['unit-tests', 'original-1', 'original-2', 'original-3', 'fixed', 'build-failed', 'unsupported', 'timeout']
assert gate['passed'] and len(rows) == len(gate['cases']) == 8
assert [r['case'] for r in rows] == expected_names
for case, row in zip(gate['cases'], rows):
    assert case['passed'] and row['passed'] == 'True'
    assert all(str(case.get(k, '')) == row[k] for k in ('case', 'exit_code', 'detector_status', 'trace_id', 'error'))
before = load('fixture-before.json')
assert before == load('fixture-after.json')
source_prefix = 'A-buildchecker/fixtures/md-rd/'
assert before == {p[len(source_prefix):]: hashlib.sha256(b).hexdigest()
                  for p, b in members(files['source.tar']).items() if p.startswith(source_prefix)}
reports = {n: load('gate/' + n + '/evidence/findings.json') for n in expected_names[1:]}
for n, report in reports.items():
    prefix = 'evidence/gate/' + n + '/fixture/'
    assert report['input_sha256'] == {p[len(prefix):]: hashlib.sha256(b).hexdigest()
                                      for p, b in files.items() if p.startswith(prefix)}
assert len({r['trace_id'] for r in reports.values()}) == 7
for n in expected_names[1:4]:
    r = reports[n]
    assert r['input_sha256'] == before
    assert r['clean_exit_code'] == r['build_exit_code'] == 0
    assert len(r['findings']) == 2
    assert {(f['type'], f['target'], f['dependency']) for f in r['findings']} == {
        ('MISSING', 'main.o', 'config.h'), ('REDUNDANT', 'main.o', 'unused.h')}
    processes = {p['pid']: p for p in load('gate/' + n + '/evidence/processes.json')}
    for f in r['findings']:
        for anchor in f['evidence']:
            prefix = 'evidence/gate/' + n + '/evidence/'
            if anchor['source'] == 'system_call':
                assert anchor['trace_file'] == 't.' + str(anchor['pid'])
                assert processes[anchor['pid']]['job_pid'] == 13
                line = files[prefix + 'trace/' + anchor['trace_file']].decode().splitlines()[anchor['line'] - 1]
                assert line.startswith(anchor['operation'] + '(')
            else:
                line = files[prefix + anchor['artifact']].decode().splitlines()[anchor['line'] - 1]
                assert line == anchor['declaration']
fixed = reports['fixed']
assert set(fixed['input_sha256']) == set(before)
assert [n for n in before if fixed['input_sha256'][n] != before[n]] == ['Makefile']
old = files['evidence/gate/original-1/fixture/Makefile'].decode().splitlines()
new = files['evidence/gate/fixed/fixture/Makefile'].decode().splitlines()
assert new == [line.replace('main.o: main.c unused.h', 'main.o: main.c config.h') for line in old]
assert fixed['findings'] == [] and fixed['clean_exit_code'] == fixed['build_exit_code'] == 0
failed = reports['build-failed']
assert failed['error_code'] == 'CHECK_FAILED' and failed['build_exit_code'] == 2
assert 'config.h' not in failed['input_sha256']
assert b'fatal error: config.h: No such file' in files['evidence/gate/build-failed/evidence/build-stderr.log']
assert reports['unsupported']['error_code'] == 'UNSUPPORTED' and reports['unsupported']['build_exit_code'] == 0
assert reports['timeout']['status'] == 'TIMED_OUT' and reports['timeout']['error_code'] == 'TIMEOUT'
assert b'execve("/usr/bin/sleep", ["sleep", "10"]' in files['evidence/gate/timeout/evidence/trace/t.13']
print(json.dumps({'passed': True, 'package_sha256': digest, 'manifest_files': len(manifest),
    'recursively_scanned_files': scanned, 'sensitive_pattern_hits': 0, 'source_sha': source_sha,
    'service_tests': 21, 'independent_tests': 6, 'gate_rows': 8,
    'original_three_hashes_equal': True, 'fixed_only_makefile_changed': True,
    'trace_and_declaration_anchors_verified': True}, indent=2))
