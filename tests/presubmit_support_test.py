from unittest import mock
import subprocess2
from testing_support import fake_repos
class ProvidedDiffChangeFakeRepo(fake_repos.FakeReposBase):

    NB_GIT_REPOS = 1

    def populateGit(self):
        self._commit_git(
            'repo_1', {
                'to_be_modified': 'please change me\n',
                'to_be_deleted': 'delete\nme\n',
                'somewhere/else': 'not a top level file!\n',
            })
        self._commit_git(
            'repo_1', {
                'to_be_modified': 'changed me!\n',
                'to_be_deleted': None,
                'somewhere/else': 'still not a top level file!\n',
                'added': 'a new file\n',
            })


class ProvidedDiffChangeTest(fake_repos.FakeReposTestBase):

    FAKE_REPOS_CLASS = ProvidedDiffChangeFakeRepo

    def setUp(self):
        super(ProvidedDiffChangeTest, self).setUp()
        self.enabled = self.FAKE_REPOS.set_up_git()
        if not self.enabled:
            self.skipTest('git fake repos not available')
        self.repo = os.path.join(self.FAKE_REPOS.git_base, 'repo_1')
        diff = subprocess2.check_output(['git', 'show'],
                                        cwd=self.repo).decode('utf-8')
        self.change = self._create_change(diff)

    def _create_change(self, diff):
        with gclient_utils.temporary_file() as tmp:
            gclient_utils.FileWrite(tmp, diff)
            options = mock.Mock(root=self.repo,
                                all_files=False,
                                generate_diff=False,
                                description='description',
                                files=None,
                                diff_file=tmp)
            change = presubmit_support._parse_change(None, options)
            assert isinstance(change, presubmit_support.ProvidedDiffChange)
            return change

    def _get_affected_file_from_name(self, change, name):
        for file in change._affected_files:
            if file.LocalPath() == os.path.normpath(name):
                return file
        self.fail(f'No file named {name}')

    def _test(self, name, old, new):
        affected_file = self._get_affected_file_from_name(self.change, name)
        self.assertEqual(affected_file.OldContents(), old)
        self.assertEqual(affected_file.NewContents(), new)

    def test_old_contents_of_added_file_returns_empty(self):
        self._test('added', [], ['a new file'])

    def test_old_contents_of_deleted_file_returns_whole_file(self):
        self._test('to_be_deleted', ['delete', 'me'], [])

    def test_old_contents_of_modified_file(self):
        self._test('to_be_modified', ['please change me'], ['changed me!'])

    def test_old_contents_of_file_with_nested_dirs(self):
        self._test('somewhere/else', ['not a top level file!'],
                   ['still not a top level file!'])

    def test_old_contents_of_bad_diff_raises_runtimeerror(self):
        diff = """
diff --git a/foo b/foo
new file mode 100644
index 0000000..9daeafb
--- /dev/null
+++ b/foo
@@ -0,0 +1 @@
+add
"""
        change = self._create_change(diff)
        with self.assertRaises(RuntimeError):
            change._affected_files[0].OldContents()

