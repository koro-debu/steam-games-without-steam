# Updating a Cracked Game

What happens to your setup when a new build ships, and what has to be redone. This is the part
everyone gets wrong once: an update doesn't just overwrite the game, it silently puts back the
files you replaced.

---

## First: is Steam going to update it for you?

Two very different situations, and they decide everything else.

| Where the game lives | What happens on update |
|---|---|
| Inside `steamapps\common\`, on an account that owns it | **Steam updates it and overwrites your emulator DLL**, usually the moment you launch the client. The game breaks and looks like it broke on its own |
| Anywhere else — a folder you copied out, or a depot you downloaded | Nothing happens. Ever. It stays on that build until you replace it by hand |

If you own the game and want to keep a working setup, **copy the folder out of the Steam library
first**. A crack living inside `steamapps\common\` is on borrowed time.

> Set the game to *Only update this game when I launch it* in its Steam properties if you must keep
> it there. It buys time; it isn't a fix.

---

## Before you touch anything

Back up these, in this order of importance:

1. **`steam_settings\`** — your AppID, interfaces, configs, DLC list. Rebuilding it is the tedious
   part; copying it is five seconds.
2. **Saves, if they're inside the game folder.** They usually aren't — gbe_fork writes to
   `%APPDATA%\GSE Saves\` by default. But if you set `local_save_path=./` as described in the
   [Goldberg guide](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md), your saves are sitting
   in the folder you're about to overwrite. Check before, not after.
3. **A list of what you added.** Usually: `steam_api64.dll`, `steam_api64_o.dll`,
   `steam_settings\`, and for EOS games `EOSSDK-Win64-Shipping.yes` plus the proxy.

---

## Getting the new build

If you own it: Steam, or [DepotDownloader](DepotDownloader.md) into a clean folder.

If you don't: the same route as the first time, via the game's thread — see the
[generic guide](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md).

Download the new build **next to** the old folder rather than over it. Two folders side by side let
you diff them, and let you fall back when the new build turns out to be worse.

---

## Redoing the setup

In order:

### 1. The Steam API layer

Copy the emulator DLL back in, after renaming the new original to `steam_api64_o.dll`.

**Regenerate `steam_interfaces.txt` from the new original DLL.** Don't reuse the old one. Games do
change the Steam API interface versions they're built against between builds, and a stale
interfaces file is the classic "it worked yesterday, now it silently won't start".

### 2. `steam_settings\`

Copy your backup back in. If you also updated gbe_fork itself, skim the new
`configs.*.EXAMPLE.ini`: key names have moved between versions, and a config the emulator no longer
recognises is ignored without a word.

### 3. The EOS layer, if the game uses it

What Steam overwrites is the file *named* `EOSSDK-Win64-Shipping.dll` — which is your proxy. The new
real SDK lands under that name, and the old `EOSSDK-Win64-Shipping.yes` is left untouched, because
Steam has no idea what it is.

That leaves a trap: **drop the proxy back in without redoing the rename and it will load the previous
build's SDK** from that stale `.yes`. It starts, it logs, and it fails in ways that make no sense.

So, in this order: delete the old `.yes`, rename the new `EOSSDK-Win64-Shipping.dll` to `.yes`, then
put the proxy back under the original name. On a freshly downloaded folder there's no stale file and
it's just the normal install from the [EOS Proxy guide](../multiplayer/EOS%20Proxy%20Usage%20Guide.md).

Check that `epic_proxy.log` appears on the next launch — the one-second confirmation that the proxy
is loaded again.

### 4. SteamStub, if it applied

If you needed [Steamless](../running/Steamless%20Usage%20Guide.md) before, the new executable is wrapped again.
Re-unpack the new one. Keeping the old unpacked `.exe` is not a shortcut: executable and game data
are versioned together, so an old binary against new data fails, usually at startup.

---

## When it doesn't work after an update

Work down this list before assuming the new build is the problem:

| Symptom | Most likely cause |
|---|---|
| Won't start, no error | Stale `steam_interfaces.txt` — regenerate it from the *new* original DLL |
| "Steam must be running" | The update restored a SteamStub-wrapped executable |
| Starts, multiplayer dead | EOS layer not reapplied — check for `epic_proxy.log` |
| EOS multiplayer fails in odd ways | The proxy is loading a stale `.yes` from the previous build |
| Starts, but it's a fresh save | `local_save_path` was pointing inside the folder you replaced |
| Everything is back to vanilla | Steam updated it in place — move the folder out of the library |

---

## Skipping the update

Nothing forces you to update. If the current build works and the new one brings nothing you want,
staying put is a legitimate choice — and for anything multiplayer, staying on the build your friends
are on matters more than being current.

Keep the old folder archived somewhere before moving on. Getting a specific past build back is
[difficult on purpose](DepotDownloader.md#old-builds-are-not-guaranteed): once it's gone from your
disk, it may be gone for good.
