#!/usr/bin/env bash
# Installs proton-autotune for the current user and enables the weekly timer + new-game trigger.
set -euo pipefail
cd "$(dirname "$0")"

python3 -c "import vdf" 2>/dev/null || {
    echo "Missing python-vdf. Arch: sudo pacman -S python-vdf   Debian/Ubuntu: sudo apt install python3-vdf   other: pip install --user vdf"
    exit 1
}

steam=""
for d in ~/.local/share/Steam ~/.steam/steam ~/.var/app/com.valvesoftware.Steam/.local/share/Steam; do
    [ -d "$d/steamapps" ] && { steam=$(readlink -f "$d"); break; }
done
[ -n "$steam" ] || { echo "No Steam installation found."; exit 1; }

install -Dm755 proton-autotune ~/.local/bin/proton-autotune
mkdir -p ~/.config/systemd/user
install -m644 systemd/proton-autotune.service systemd/proton-autotune.timer ~/.config/systemd/user/
sed "s|^PathChanged=.*|PathChanged=$steam/appcache/librarycache|" systemd/proton-autotune.path \
    > ~/.config/systemd/user/proton-autotune.path

systemctl --user daemon-reload
systemctl --user enable --now proton-autotune.timer proton-autotune.path
echo "Installed. Preview what it would change:  proton-autotune --dry-run"
