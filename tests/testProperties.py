import os
import unittest
from unittest import mock

import support
from support import (FakeNemoFile, makeDirectory, makeRepository, requiresGit,
                     resetSharedState, writeFile)

plugin = support.importPlugin("nemoRepoProperties")

from nemoRepoCore import LastCommit, RepoInfo, repoCache


class FakeGrid:

    def __init__(self):
        self.rows = []
        self.shown = False

    def show_all(self):
        self.shown = True


def recordRow(grid, row, labelText, valueText):
    grid.rows.append((row, labelText, valueText))
    return row + 1


def fakePropertyPage(**properties):
    return properties


def fakeLabel(label):
    return label


class PropertiesTestCase(unittest.TestCase):

    def setUp(self):
        resetSharedState()
        self.addCleanup(resetSharedState)
        for name, replacement in (("_addRow", recordRow), ("_buildGrid", FakeGrid)):
            patcher = mock.patch.object(plugin, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)
        for owner, name, replacement in ((plugin.Nemo, "PropertyPage", fakePropertyPage),
                                         (plugin.Gtk, "Label", fakeLabel)):
            patcher = mock.patch.object(owner, name, replacement)
            patcher.start()
            self.addCleanup(patcher.stop)

    def rowsFor(self, info, root="/repo"):
        grid = FakeGrid()
        plugin._fillGrid(grid, root, info)
        return [(label, value) for _, label, value in grid.rows]


class FillGridTests(PropertiesTestCase):

    def makeInfo(self):
        info = RepoInfo("/repo")
        info.branch = "feature/parser"
        info.upstream = "origin/feature/parser"
        info.hasUpstream = True
        info.ahead = 2
        info.staged = 1
        info.unstaged = 3
        info.lastCommit = LastCommit("a1b2c3d", "Author", "2 hours ago", "fix the parser")
        return info

    def testFullState(self):
        self.assertEqual(self.rowsFor(self.makeInfo()), [
            ("Repository", "/repo"),
            ("Branch", "feature/parser"),
            ("Upstream", "origin/feature/parser"),
            ("Ahead / behind", "2 ahead, 0 behind"),
            ("Staged changes", "1"),
            ("Unstaged changes", "3"),
            ("Untracked files", "0"),
            ("Summary", "2 ahead, 4 changed"),
            ("Last commit", "a1b2c3d  fix the parser"),
            ("", "by Author, 2 hours ago"),
        ])

    def testRowNumbersAreSequential(self):
        grid = FakeGrid()
        plugin._fillGrid(grid, "/repo", self.makeInfo())
        self.assertEqual([row for row, _, _ in grid.rows], list(range(10)))

    def testNoUpstream(self):
        info = self.makeInfo()
        info.hasUpstream = False
        info.upstream = None
        self.assertIn(("Upstream", "(none)"), self.rowsFor(info))

    def testDetachedBranch(self):
        info = self.makeInfo()
        info.branch = None
        self.assertIn(("Branch", "(detached)"), self.rowsFor(info))

    def testNoCommitsYet(self):
        info = self.makeInfo()
        info.lastCommit = None
        rows = self.rowsFor(info)
        self.assertEqual(rows[-1][0], "Summary")
        self.assertEqual(len(rows), 8)

    def testErrorShowsOnlyStatus(self):
        info = RepoInfo("/repo")
        info.error = "git status failed"
        self.assertEqual(self.rowsFor(info), [("Status", "git status failed")])


class PropertyPageTests(PropertiesTestCase):

    def testSeveralSelectedFolders(self):
        files = [FakeNemoFile(makeDirectory()), FakeNemoFile(makeDirectory())]
        self.assertEqual(plugin.RepoPropertyPageProvider().get_property_pages(files), [])

    def testPlainFolder(self):
        files = [FakeNemoFile(makeDirectory())]
        self.assertEqual(plugin.RepoPropertyPageProvider().get_property_pages(files), [])

    def testRegularFile(self):
        path = writeFile(makeDirectory(), "file.txt")
        files = [FakeNemoFile(path, isDirectory=False)]
        self.assertEqual(plugin.RepoPropertyPageProvider().get_property_pages(files), [])

    def testRemoteFolder(self):
        files = [FakeNemoFile("/share", scheme="sftp")]
        self.assertEqual(plugin.RepoPropertyPageProvider().get_property_pages(files), [])

    def testNameAndDescription(self):
        [entry] = plugin.RepoPropertyPageProvider().get_name_and_desc()
        self.assertTrue(entry.startswith("nemo-repo-properties:::"))


@requiresGit
class RepositoryPageTests(PropertiesTestCase):

    def testPageForRepositoryRoot(self):
        repository = makeRepository()
        [page] = plugin.RepoPropertyPageProvider().get_property_pages([FakeNemoFile(repository)])
        self.assertEqual(page["name"], "NemoRepoProperties::git")
        self.assertEqual(page["label"], "Git")
        self.assertTrue(page["page"].shown)
        rows = dict((label, value) for _, label, value in page["page"].rows)
        self.assertEqual(rows["Repository"], repository)
        self.assertEqual(rows["Branch"], "main")
        self.assertEqual(rows["Upstream"], "(none)")
        self.assertEqual(rows["Last commit"].split("  ", 1)[1], "initial commit")

    def testFolderInsideRepository(self):
        repository = makeRepository()
        nested = os.path.join(repository, "src")
        os.mkdir(nested)
        files = [FakeNemoFile(nested)]
        self.assertEqual(plugin.RepoPropertyPageProvider().get_property_pages(files), [])

    def testPageIgnoresCachedState(self):
        repository = makeRepository()
        repoCache.get(repository)
        writeFile(repository, "untracked.txt")
        [page] = plugin.RepoPropertyPageProvider().get_property_pages([FakeNemoFile(repository)])
        rows = dict((label, value) for _, label, value in page["page"].rows)
        self.assertEqual(rows["Untracked files"], "1")
        self.assertTrue(repoCache.get(repository).dirty)


if __name__ == "__main__":
    unittest.main()
