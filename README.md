# nemo-repo-properties

nemo-repo-properties is an extension for [Nemo](https://github.com/linuxmint/nemo),
the Cinnamon file manager, that adds a "Git" tab to the Properties dialog of a
repository folder. The tab shows the branch, its upstream, how far ahead or
behind it is, the working tree counts and the last commit. It is a plugin for
**nemo-repo-core** and needs it installed.

## Features

- A Git tab next to Basic and Permissions, for example:

  ```
  Repository       /home/you/code/project
  Branch           feature/parser
  Upstream         origin/feature/parser
  Ahead / behind   2 ahead, 0 behind
  Staged changes   1
  Unstaged changes 3
  Untracked files  0
  Summary          2 ahead, 4 changed
  Last commit      a1b2c3d  fix the token boundary case
                   by You, 2 hours ago
  ```

- Upstream shows `(none)` when the branch tracks nothing; the last commit rows
  are left out in a repository without commits.
- When git cannot read the repository, the tab shows a single Status row with
  the reason.
- Every value is selectable, so a branch name or commit hash can be copied
  straight out of the dialog.
- Opening the dialog always asks git for the current state, ignoring the cache
  TTL, and stores the fresh result in the shared cache.

## Requirements

- nemo-repo-core 0.1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install and run

Install nemo-repo-core first (run `./install.sh` in its checkout), then from a
checkout of this repository:

```bash
./install.sh
nemo -q
```

`install.sh` links `nemoRepoProperties.py` into
`~/.local/share/nemo-python/extensions` and checks that it imports. Pass
`--copy` to copy instead of link. It stops with a message if nemo-repo-core is
not installed. No root is required.
`./uninstall.sh` removes the plugin.

## Configuration

None of its own, so there is no `config.example.json`. Core settings from
`~/.config/nemo-repo-core.json`, such as `log_level`, still apply.

## Tests

The tests use the standard library `unittest` and need PyGObject with the Nemo
and Gtk 3 typelibs and nemo-repo-core: an installed core, a checkout of
nemo-repo-core next to this one (`../nemo-repo-core`), or a path in
`NEMO_REPO_CORE_PATH`. Without the core the suite is skipped. Run them from the
repository root:

```bash
python3 -m unittest discover -s tests
```

They cover the rows of the Git tab for complete, detached, upstream-less,
commit-less and failing repositories, which selections get a tab, and that
opening the dialog bypasses the cache. Gtk widgets are replaced by stubs, so no
display is needed. Tests that need git create throwaway repositories in a
temporary directory and are skipped when `git` is not installed. The shared
config is redirected to a temporary file, so your real config is never
touched.

## Project layout

```
nemoRepoProperties.py     the Nemo extension
install.sh, uninstall.sh  per-user install
tests/
  support.py              temporary config, git helpers and core lookup
  testProperties.py       unittest suite
```

## Limitations

- The tab appears only for a single selected local folder that is a
  repository root, not for folders inside a checkout.
- The values are read once when the dialog opens and do not update while it
  stays open.

## License

MIT. See `LICENSE`.
