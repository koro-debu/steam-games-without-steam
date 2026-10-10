# Steam Achievement Manager (SAM) — Usage Guide

SAM is an open-source tool that unlocks, re-locks or hides achievements on **your own** Steam
account, for games already in your library.

Unlike the other guides in this repo, SAM works *with* Steam, not around it: the client must be
running and logged in.

---

## Read this first

- **VAC games: never.** Do not point SAM at a competitive multiplayer title protected by VAC
  (CS2, Dota 2, TF2, …). A VAC ban is permanent and irreversible.
- **It violates the Steam Subscriber Agreement.** Valve tolerates it in practice on single-player
  games, but that's tolerance, not permission — the account risk is yours.
- **Library only.** SAM cannot touch a game you don't own.

---

## Download

Official repository: https://github.com/gibbed/SteamAchievementManager

Grab the latest `SteamAchievementManager-<version>.zip` from **Releases** and extract it to a
dedicated folder, e.g. `C:\Tools\SAM\`.

The archive is tiny (about 55 KB) and contains five files:

| File | Role |
|---|---|
| `SAM.Picker.exe` | the game list — **this is the one you launch** |
| `SAM.Game.exe` | the achievement editor; launched by the picker with an AppID argument |
| `SAM.API.dll` | the Steam client bindings both executables use — keep it next to them |
| `LICENSE.txt`, `git-log.txt` | licence and the commit log of the build |

> Running `SAM.Game.exe` on its own does nothing useful — it expects an AppID on the command line.

**Requirements:** .NET Framework **4.8** — that's what 7.0.41 targets, checked in the binary
itself, not .NET 8. Windows 10 1903 and later ship 4.8, so on any current install there is nothing
to download. Only if SAM refuses to start with a framework error do you need
[the 4.8 runtime](https://dotnet.microsoft.com/download/dotnet-framework/net48) from Microsoft.

---

## Preparation

1. **Antivirus.** SAM is commonly flagged as `HackTool` / `RiskWare`. That's a false positive on
   the official build — add `C:\Tools\SAM\` to your exclusions before running it.
2. **Steam.** Fully exit Steam (tray icon → *Exit Steam*), restart it, and log in.
3. **Put some playtime on the game.** Launch it and play a few minutes before unlocking anything.
   Achievements can be rolled back server-side when they land on an account with near-zero
   playtime — see [Achievements re-lock](#achievements-re-lock-after-a-while) below.
4. Close the game. **Leave Steam running.**

---

## Usage

### 1. Launch the picker

Right-click `SAM.Picker.exe` → **Run as administrator** (avoids permission errors).
A window lists every game in your library.

### 2. Pick the game

Search or scroll, then double-click it. The achievement editor opens.

### 3. Edit

| Goal | Action |
|---|---|
| Unlock everything | **Unlock All** |
| Unlock specific ones | tick the individual boxes |
| Hide an already-earned achievement | untick its box |

### 4. Save — this is the step everyone forgets

Click **Commit Changes** at the bottom of the window. Closing the window without it discards
everything.

A Steam toast should pop in the corner for each unlock.

### 5. Verify

Close SAM, restart Steam, then check *Profile → Games → Achievements*.

---

## Troubleshooting

### The game isn't in the list

Make sure it's installed and visible in your library, then restart Steam and relaunch SAM as
administrator.

### Achievements re-lock after a while

Steam's servers can revert an achievement that's wildly inconsistent with your recorded
playtime — a "100 hours played" achievement on an account with 5 minutes, for instance.

Play the game long enough to make the unlock plausible, or unlock in batches over several
sessions instead of all at once.

### SAM won't start (.NET error)

Install .NET Framework 4.8. This should not happen on Windows 10 1903+ or Windows 11, where it's
part of the OS.

---

## Limits

- **Achievements only.** SAM does not touch in-game progression (money, items, levels). That
  means editing save files, which is a different job.
- **Steam Cloud.** Changes sync, but if you launch the game afterwards and it re-synchronises its
  own achievement state, it can overwrite what SAM did.

---

## Links

- Repository: https://github.com/gibbed/SteamAchievementManager
- Releases: https://github.com/gibbed/SteamAchievementManager/releases
- Issues: https://github.com/gibbed/SteamAchievementManager/issues
