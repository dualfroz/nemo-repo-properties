#!/usr/bin/python3
import importlib.util
import os
import sys


def _ensureCoreOnPath():
    if importlib.util.find_spec("nemoRepoCore") is not None:
        return
    dataHome = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    dataDirs = (os.environ.get("XDG_DATA_DIRS") or "/usr/local/share:/usr/share").split(":")
    for base in [dataHome] + dataDirs:
        candidate = os.path.join(base, "nemo-repo-core")
        if os.path.isdir(os.path.join(candidate, "nemoRepoCore")):
            sys.path.insert(0, candidate)
            return


_ensureCoreOnPath()

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Nemo", "3.0")
from gi.repository import GObject, Gtk, Nemo

from nemoRepoCore import (findRepoRoot, repoCache, requireCore,
                          singleLocalDirectory)

requireCore("0.1.0")


def _buildGrid():
    grid = Gtk.Grid()
    grid.set_row_spacing(6)
    grid.set_column_spacing(12)
    grid.set_margin_start(12)
    grid.set_margin_end(12)
    grid.set_margin_top(12)
    grid.set_margin_bottom(12)
    return grid


def _addRow(grid, row, labelText, valueText):
    label = Gtk.Label(label=labelText)
    label.set_xalign(0)
    label.get_style_context().add_class("dim-label")
    value = Gtk.Label(label=valueText)
    value.set_xalign(0)
    value.set_selectable(True)
    value.set_line_wrap(True)
    grid.attach(label, 0, row, 1, 1)
    grid.attach(value, 1, row, 1, 1)
    return row + 1


def _fillGrid(grid, repoRoot, info):
    if info.error:
        _addRow(grid, 0, "Status", info.error)
        return

    row = 0
    row = _addRow(grid, row, "Repository", repoRoot)
    row = _addRow(grid, row, "Branch", info.branchLabel)
    row = _addRow(grid, row, "Upstream", info.upstream if info.hasUpstream else "(none)")
    row = _addRow(grid, row, "Ahead / behind",
                  "%d ahead, %d behind" % (info.ahead, info.behind))
    row = _addRow(grid, row, "Staged changes", str(info.staged))
    row = _addRow(grid, row, "Unstaged changes", str(info.unstaged))
    row = _addRow(grid, row, "Untracked files", str(info.untracked))
    row = _addRow(grid, row, "Summary", info.summary)
    if info.lastCommit:
        commit = info.lastCommit
        row = _addRow(grid, row, "Last commit",
                      "%s  %s" % (commit.hash, commit.subject))
        row = _addRow(grid, row, "",
                      "by %s, %s" % (commit.author, commit.relativeDate))


class RepoPropertyPageProvider(GObject.GObject, Nemo.PropertyPageProvider,
                               Nemo.NameAndDescProvider):

    def get_property_pages(self, files):
        path = singleLocalDirectory(files)
        if path is None:
            return []

        repoRoot = findRepoRoot(path)
        if repoRoot is None:
            return []

        info = repoCache.refresh(repoRoot)

        grid = _buildGrid()
        _fillGrid(grid, repoRoot, info)
        grid.show_all()

        return [Nemo.PropertyPage(name="NemoRepoProperties::git",
                                  label=Gtk.Label(label="Git"),
                                  page=grid)]

    def get_name_and_desc(self):
        return ["nemo-repo-properties:::Git tab in the folder Properties dialog"]
