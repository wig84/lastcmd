# lastcmd

Project initialized with project-init.

## Welcome

**Project:** lastcmd

**Description:** Unix-style terminal pipe sink that copies command output to the system clipboard while keeping the output visible in the terminal.

**Commands:**

```bash
ls -la | lastcmd
pytest -q | lastcmd
git diff | lastcmd
```

## Requirements

The command uses the first available clipboard backend:

- `wl-copy` from `wl-clipboard`
- `xclip`
- `xsel`

On Ubuntu with X11, install `xclip` if none is available:

```bash
sudo apt install xclip
```
