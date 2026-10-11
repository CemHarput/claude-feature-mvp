import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]

class MVPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'mvp-test@example.invalid')
        self.git('config', 'user.name', 'MVP Test')
        self.install()
        (self.repo / 'app.txt').write_text('baseline\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')
        self.helper = self.repo / '.claude/scripts/feature_state.py'

    def call(self, args, success=True):
        p = subprocess.run(args, cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(p.returncode == 0, success, p.stdout + p.stderr)
        return p

    def git(self, *args):
        return self.call(['git', *args])

    def install(self, success=True):
        return self.call([sys.executable, str(PACKAGE / 'install.py'), str(self.repo)], success)

    def state(self, *args, success=True):
        return self.call([sys.executable, str(self.helper), *args], success)

    def plan(self, slug='sample'):
        self.state('init', slug)
        d = self.repo / 'docs/features' / slug
        (d / 'request.md').write_text('Add behavior\n')
        (d / 'plan.md').write_text('READY\nAC1: observable behavior\n')
        self.state('planned', slug)
        return hashlib.sha256((d / 'plan.md').read_bytes()).hexdigest()

    def test_full_lifecycle_and_optional_review(self):
        h = self.plan()
        self.state('start', 'sample', '--plan-hash', h)
        (self.repo / 'app.txt').write_text('implemented\n')
        d = self.repo / 'docs/features/sample'
        self.state('finish', 'sample', '--result', 'implemented', success=False)
        (d / 'implementation.md').write_text('AC1 met; tests pass\n')
        s = json.loads(self.state('finish', 'sample', '--result', 'implemented').stdout)
        self.assertEqual(s['review'], 'not_requested')
        (d / 'review.md').write_text('PASS\n')
        s = json.loads(self.state('reviewed', 'sample').stdout)
        self.assertEqual(s['review'], 'completed')
        self.assertTrue(s['approval_matches'])

    def test_dirty_source_and_untracked_are_blocked(self):
        h = self.plan()
        (self.repo / 'new-source.py').write_text('print(1)\n')
        self.state('start', 'sample', '--plan-hash', h, success=False)
        (self.repo / 'new-source.py').unlink()
        (self.repo / 'app.txt').write_text('user edit\n')
        self.state('start', 'sample', '--plan-hash', h, success=False)

    def test_approval_hash_and_post_start_mutation(self):
        h = self.plan()
        self.state('start', 'sample', '--plan-hash', 'wrong', success=False)
        self.state('start', 'sample', '--plan-hash', h)
        (self.repo / 'docs/features/sample/plan.md').write_text('different plan\n')
        self.state('check', 'sample', success=False)
        h2 = hashlib.sha256((self.repo / 'docs/features/sample/plan.md').read_bytes()).hexdigest()
        self.state('start', 'sample', '--plan-hash', h2, success=False)

    def test_resume_blocked_and_concurrent_feature_guard(self):
        h = self.plan()
        self.state('start', 'sample', '--plan-hash', h)
        (self.repo / 'app.txt').write_text('partial\n')
        self.state('start', 'sample', '--plan-hash', h)
        (self.repo / 'docs/features/sample/implementation.md').write_text('BLOCKED\n')
        self.state('finish', 'sample', '--result', 'blocked')
        h2 = self.plan('second')
        self.state('start', 'second', '--plan-hash', h2, success=False)
        self.state('start', 'sample', '--plan-hash', h)
        self.assertEqual((self.repo / 'app.txt').read_text(), 'partial\n')

    def test_head_change_blocked(self):
        h = self.plan()
        self.state('start', 'sample', '--plan-hash', h)
        self.git('commit', '--allow-empty', '-qm', 'unexpected commit')
        self.state('check', 'sample', success=False)

    def test_slug_and_duplicate_guard(self):
        self.state('init', '../escape', success=False)
        self.state('init', 'UPPER', success=False)
        self.state('init', 'sample')
        self.state('init', 'sample', success=False)
        self.state('planned', 'sample', success=False)

    def test_installer_idempotent_and_preserves_existing_settings(self):
        settings = self.repo / '.claude/settings.json'
        settings.write_text('{"permissions":{"defaultMode":"default"},"env":{"CUSTOM":"yes"}}\n')
        before = settings.read_bytes()
        self.install()
        self.install()
        self.assertEqual(settings.read_bytes(), before)
        self.assertEqual((self.repo / 'CLAUDE.md').read_text().count('<!-- claude-feature-mvp -->'), 1)

    def test_installer_conflict_preflight_no_partial_write(self):
        command = self.repo / '.claude/commands/feature-plan.md'
        command.write_text('user command\n')
        missing = self.repo / '.claude/agents/architecture-planner.md'
        missing.unlink()
        self.install(success=False)
        self.assertFalse(missing.exists())
        self.assertEqual(command.read_text(), 'user command\n')

if __name__ == '__main__':
    unittest.main()
