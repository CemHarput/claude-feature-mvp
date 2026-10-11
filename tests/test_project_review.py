import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]

class ProjectReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.run_command(['git','init','-q'])
        self.run_command(['git','config','user.email','review@example.invalid'])
        self.run_command(['git','config','user.name','Review Test'])
        self.run_command([sys.executable,str(PACKAGE/'install.py'),str(self.repo)])
        (self.repo/'src').mkdir()
        (self.repo/'src/a.py').write_text('print(1)\n')
        (self.repo/'src/b.py').write_text('print(2)\n')
        (self.repo/'.gitignore').write_text('ignored.txt\n')
        self.run_command(['git','add','.'])
        self.run_command(['git','commit','-qm','baseline'])

    def run_command(self,args,ok=True):
        p=subprocess.run(args,cwd=self.repo,capture_output=True,text=True)
        self.assertEqual(p.returncode==0,ok,p.stdout+p.stderr)
        return p

    def snapshot(self,scope='.',ok=True):
        p=self.run_command([sys.executable,str(self.repo/'.claude/scripts/project_review_snapshot.py'),'snapshot',scope],ok)
        return json.loads(p.stdout) if ok else None

    def test_hash_changes_on_source_but_not_report_writes(self):
        before=self.snapshot()
        d=self.repo/'docs/reviews/run'; d.mkdir(parents=True)
        (d/'report.md').write_text('report')
        self.assertEqual(before['fingerprint'],self.snapshot()['fingerprint'])
        (self.repo/'src/a.py').write_text('print(3)\n')
        self.assertNotEqual(before['fingerprint'],self.snapshot()['fingerprint'])

    def test_scoped_and_new_files_and_exclusions(self):
        (self.repo/'src/new file.py').write_text('print(4)\n')
        (self.repo/'ignored.txt').write_text('ignored')
        (self.repo/'node_modules').mkdir()
        (self.repo/'node_modules/third-party.js').write_text('vendor')
        s=self.snapshot('src')
        self.assertEqual({x['path'] for x in s['files']},{'src/a.py','src/b.py','src/new file.py'})
        all_files=self.snapshot()
        self.assertNotIn('ignored.txt',{x['path'] for x in all_files['files']})
        self.assertIn('node_modules/third-party.js',{x['path'] for x in all_files['excluded']})

    def test_rejects_outside_missing_and_symlink_scope(self):
        self.snapshot('../other',ok=False)
        self.snapshot('/tmp',ok=False)
        self.snapshot('missing',ok=False)
        (self.repo/'linked').symlink_to(self.repo/'src',target_is_directory=True)
        self.snapshot('linked',ok=False)

    def test_config_and_new_source_change_fingerprint(self):
        before=self.snapshot()['fingerprint']
        p=self.repo/'.claude/project-review.json'
        c=json.loads(p.read_text()); c['batch_size']=10; p.write_text(json.dumps(c))
        self.assertNotEqual(before,self.snapshot()['fingerprint'])
        before=self.snapshot()['fingerprint']
        (self.repo/'src/new.py').write_text('print(5)\n')
        self.assertNotEqual(before,self.snapshot()['fingerprint'])

    def test_deleted_binary_oversized_and_symlink_visible(self):
        (self.repo/'src/a.py').unlink()
        (self.repo/'src/data.bin').write_bytes(bytes([0,1,2]))
        (self.repo/'src/large.txt').write_text('x'*524289)
        (self.repo/'src/link').symlink_to(self.repo/'src/b.py')
        kinds={x['path']:x['kind'] for x in self.snapshot()['files']}
        self.assertEqual(kinds['src/a.py'],'missing')
        self.assertEqual(kinds['src/data.bin'],'binary')
        self.assertEqual(kinds['src/large.txt'],'oversized')
        self.assertEqual(kinds['src/link'],'symlink')

    def test_refactor_implementer_is_installed_with_safety_contract(self):
        agent = (self.repo/'.claude/agents/refactor-implementer.md').read_text()
        self.assertIn('name: refactor-implementer', agent)
        self.assertIn('explicitly supplied by', agent)
        self.assertIn('preserve all user changes', agent)
        self.assertIn('Do not silently broaden the scope', agent)
        self.assertIn('NEEDS_PLAN', agent)

if __name__=='__main__': unittest.main()
