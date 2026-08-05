# nemo-repo-properties

A "Git" tab in the folder Properties dialog of
[Nemo](https://github.com/linuxmint/nemo), the Cinnamon file manager.

Right click a repository, choose Properties, and next to Basic and Permissions
there is a Git tab:

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

Every value is selectable, so a branch name or a commit hash can be copied
straight out of the dialog.

The tab only appears on repository roots. On any other folder the Properties
dialog is unchanged.

## Requirements

- [nemo-repo-core](https://github.com/dualfroz/nemo-repo-core) 1.x
- Nemo with `nemo-python`, `git` in `PATH`

## Install

```bash
git clone https://github.com/dualfroz/nemo-repo-core
cd nemo-repo-core && ./install.sh && cd ..

git clone https://github.com/dualfroz/nemo-repo-properties
cd nemo-repo-properties && ./install.sh

nemo -q
```

`install.sh` links the plugin into `~/.local/share/nemo-python/extensions` and
checks that it imports. Pass `--copy` to copy instead of link. `./uninstall.sh`
removes it. Nothing is written outside your home directory and no root is
required.

## Configuration

None of its own. It reads the shared file,
`~/.config/nemo-repo-core.json`, only for core settings such as `log_level`.

Opening Properties is an explicit request for the current state, so this plugin
deliberately bypasses the shared cache and asks git directly every time. The
`cache_ttl_seconds` setting does not affect it.

## Tested on

Linux Mint 22.2 (Zara), Cinnamon 6.4.14, Nemo 6.4.5, python-nemo 6.4.0,
Python 3.12.3.

## Migrating from the single file version

This tab used to be part of `nemo_repo_emblems.py`, one file that also provided
emblems, list view columns and a context menu. It is now a separate plugin on a
shared core, so it can be installed on its own.

Your config carries over automatically, and the old config file is not
modified. Remove the old extension so the tab does not appear twice:

```bash
rm ~/.local/share/nemo-python/extensions/nemo_repo_emblems.py
nemo -q
```

## License

MIT. See `LICENSE`.
