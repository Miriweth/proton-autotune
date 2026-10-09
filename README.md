# proton-autotune

Sets Steam launch options for the games in your library from ProtonDB reports, so you
don't have to look them up yourself.

It reads the public [ProtonDB data dump](https://github.com/bdefore/protondb-data), keeps
reports from the last two years where the game worked on an NVIDIA card, and counts which
launch options people used. An option goes into that game's launch options when at least
three of those reports mention it and they make up at least 30% of the game's reports. If
the reports disagree, or nobody needed anything, the game is left alone. There's no AI in
here, just counting, so every change can be traced back to the reports.

## What it does to your Steam setup

- Covers every game in your library, installed or not.
- Only touches launch options it wrote itself. Type your own launch options for a game,
  even just `%command%`, and that game is yours from then on.
- Writes `localconfig.vdf` only after Steam has exited. Steam rewrites that file from
  memory when it quits, so anything written while it runs would be lost. If Steam is open,
  the tool waits in the background and writes the moment you close it.
- Backs up `localconfig.vdf` next to the original before every change. The backups
  (`localconfig.vdf.bak-autotune-*`) are never cleaned up; delete old ones when you like.
- Skips debug and overlay options (`PROTON_LOG`, `DXVK_HUD`, `mangohud`, `gamemoderun`, ...),
  flags that need a value (`-w 1920`) and anything after a shell operator (`; pkill ...`).

It does not skip games with anti-cheat. If you play any, check the log after the first run.

## Install

Needs Python 3, [python-vdf](https://github.com/ValvePython/vdf) and `pgrep` (procps).
`notify-send` is used for a desktop notification if it's there.

```bash
git clone https://github.com/Miriweth/proton-autotune
cd proton-autotune
./install.sh
```

This copies the script to `~/.local/bin` and enables two systemd user units: a weekly
timer (missed runs are caught up after boot) and a path watcher that runs the tool when
your library changes, so new games are picked up. Native, `~/.steam/steam` and Flatpak Steam
are detected.

Rebuilding the index loads the whole ProtonDB dump and needs a few GB of RAM for about a
minute, once a week.

To see what it would change without writing anything (`~/.local/bin` has to be on your
`PATH`, otherwise call it with the full path):

```bash
proton-autotune --dry-run
```

## Files

Everything lives in `~/.local/share/proton-autotune/`:

- `log.txt`: every change, as `Game (appid): 'old' -> 'new'`
- `state.json`: the launch options this tool set, per app ID
- `index.json`, `titles.json`: the reduced ProtonDB data, refreshed weekly (about a 70 MB download)

## Settings

The thresholds are constants at the top of the script (`MIN_REPORTS`, `MIN_SHARE`,
`MAX_AGE_DAYS`). On an AMD card, run `systemctl --user edit proton-autotune.service` and add:

```ini
[Service]
Environment=PROTON_AUTOTUNE_GPU=AMD
```

## Uninstall

```bash
systemctl --user disable --now proton-autotune.timer proton-autotune.path
rm ~/.local/bin/proton-autotune ~/.config/systemd/user/proton-autotune.*
```

Launch options it already set stay in Steam. Clear them by hand if you want them gone.

## Limits

"Most common among similar setups" is not the same as "best for your machine", and nothing
gets benchmarked. A handful of reports with an unusual setup can still cross the 30% line,
for example a frame-rate cap tuned to someone else's monitor.

## License

MIT
