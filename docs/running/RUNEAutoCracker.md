# RUNEAutoCracker — Usage Guide

[RUNEAutoCracker](https://github.com/Mush-iii/RUNEAutoCracker) does the whole
[RUNE](RUNE%20Steam%20Emulator%20User%20Guide.md) page in one pass: point it at a game folder and it
finds the AppID, unpacks SteamStub if the executable needs it, installs the emulator, and writes
`steam_emu.ini` with the DLC list already filled in.

It isn't the only tool here that automates a job — [SteamAutoCrack](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#4-apply-goldberg)
drives the gbe_fork route and [CreamInstaller](../other/DLC%20Unlocking.md#doing-all-of-it-automatically)
does the DLC pass. It is the only one that automates **an emulator nobody can audit**, which is why
it gets its own set of checks below. Read [the RUNE guide](RUNE%20Steam%20Emulator%20User%20Guide.md)
first if you haven't: everything it says about provenance applies to whatever this installs.

> **For legal owners only**, as everywhere here.

---

## Do you want this?

**Try [gbe_fork](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) first.** It's the
maintained one, the readable one, and it covers nearly everything. This tool is worth reaching for
when:

- gbe_fork misbehaves on a specific game and you want the RUNE fallback without doing it by hand
- the game has a lot of DLC, which is where it genuinely saves time (see below)
- you want a crack folder produced *without* touching your install — it has a mode for that

**What it actually buys you over the manual route** is the DLC list. RUNE's DLC handling is a list of
IDs in `steam_emu.ini`, and filling it by hand means collecting them from SteamDB one at a time. This
asks the Steam store and writes them for you. On a game with twenty DLC that's the difference between
a minute and an evening.

---

## Get it, and check it

Releases: <https://github.com/Mush-iii/RUNEAutoCracker/releases>

Verified here on **2026-08-10**, version **v1.2.1**:

```
sha256  835c77cd2049e3136acb5093e93bbdbb22f00ad831a35a93e039cd694530f693  RUNEAutoCracker.zip
sha256  d3b17d1f00fabd4fe69b557b2b02da48ef8ac0965b5fe059e7d902812a8dba69  RUNEAutoCracker.exe
```

```cmd
certutil -hashfile RUNEAutoCracker.exe SHA256
```

**Nothing is pinned for it**, deliberately — it updates itself, so a pinned
copy would claim a stability the tool doesn't have. Take it from upstream and check the hash the way
the table below was produced.

| Check | Result |
|---|---|
| VirusTotal, the `.exe` | **2/66** — Bkav's generic `W32.Malware`, and APEX "Malicious". Machine heuristics, no named family |
| VirusTotal, the `.zip` | **1/52**, the same Bkav hit |
| Sandbox verdict | **clean** |
| Network | **`github.com` and `raw.githubusercontent.com` only.** No third-party host, no telemetry |
| Files written | 261, all under `Temp\_MEI…\` — PyInstaller unpacking itself, not the tool touching your system |
| Registry | one file-association key |
| Steam login | **anonymous only.** `anonymous_login()` is the single call; the word *password* does not appear in the source |
| Its bundled Steamless | **byte-identical to atom0s's official release**, checked against atom0s's release |

The `OBFUSCATED` tag VirusTotal applies is PyInstaller packing, which is also why a 107 KB script
ships as a 61 MB executable. That script is public and single-file, so you can read exactly what
you're running and rebuild it yourself instead.

---

## The three modes

They are not variations on a theme, and the names mislead. Pick **Regular** unless you have a reason.

| Mode | What it installs | Notes |
|---|---|---|
| **Regular** | RUNE's `steam_api64.dll`, plus `steam_api64.rne` and `steam_emu.ini` | What the RUNE guide describes, and the only one tested here |
| **Steakclient** | `winmm.dll`, `steakclient64.dll`, `steak_emu.ini` | A proxy DLL: Windows loads `winmm.dll` from the game folder before the system one. **x64 only** |
| **Steamclient** | `steamclient64.dll`, `rune64.dll`, `GameOverlayRenderer64.dll` | Impersonates Steam's backend rather than the game's own DLL |

**"Steakclient" is spelled with a k in the tool itself** — folder, DLL and ini all carry the author's
typo. It is a different mode from *Steamclient* sitting next to it in the same dialog, not a
misspelling of it.

> **Why Steakclient greys out.** Choosing the SteamStub *patcher* below disables it. The tool only
> says it's "unavailable" without explaining, but both features install a `winmm.dll` into the same
> folder and only one file can hold that name — which is a deduction from reading the code, not
> something upstream states.

---

## SteamStub: two ways

A setting, not a mode. `DRMMethod` is either:

- **`steamless`** (the default) — calls the bundled `Steamless.CLI.exe` and rewrites the executable on
  disk, exactly as [the Steamless guide](Steamless%20Usage%20Guide.md) describes.
- **`steamstub`** — installs a `winmm.dll` that patches the DRM **in memory** at launch instead.
  Nothing on disk is rewritten, so there's no unpacked executable to keep and nothing to redo after a
  game update. It's the thing to try when Steamless reports a variant it doesn't support.

---

## Where the output goes

Worth setting before you run it, because the default writes into the folder you pointed at:

- **In place** — the game folder is modified. Fine on a copy, and on a Steam install it survives until
  the next update.
- **Crack only** — it stages into a temporary folder and hands you just the files, leaving the game
  untouched. This is the option to use when you want to see what a crack consists of without
  committing to it.
- **Both** — applies it, and also zips the crack files.

---

## The `.rne` is your backup, and it is load-bearing

RUNEAutoCracker renames the game's own `steam_api64.dll` to `steam_api64.rne`, and RUNE forwards its
calls to that file. So unlike everywhere else in this repo, **the backup is not a spare copy — it's a
file the emulator reads at runtime.** Delete it and nothing works.

There is therefore no `_o` file on this path, and the
[naming convention](Steamless%20Usage%20Guide.md#back-up-the-executable--mandatory) should not be
imposed on it — renaming the `.rne` breaks the install.

This is also where the tool quietly does better than the manual route. Installing RUNE by hand leaves
you with the `.rne` **shipped in the package**, which is Valve's DLL but not *your game's* copy of it;
the [RUNE guide](RUNE%20Steam%20Emulator%20User%20Guide.md#installation) tells you to swap in your own
if the game misbehaves. The tool starts from yours. Re-run it on an already-patched folder and it
restores from the `.rne` first, rather than backing up a crack over a crack.

---

## Confirmed working

**Car Mechanic Simulator 2018** (AppID 645630), v1.2.1, **Regular** mode, 2026-08-10. Pointed at the
game folder, one pass, no configuration touched: the game launches with the Steam client closed and
**all DLC are present**, including the separately-bought ones. Nothing was entered by hand.

This is the first thing on the RUNE path in this repo confirmed by running it rather than by reading
files.

---

**Since then** (release thread on cs.rin.ru, to 2026-09-28): v1.2.2 came out on 2026-08-15 and is
the current release; it hasn't been re-verified here. Reported problems, none fixed yet: the Steam
lookup never finishes or answers *Could not find game* on some titles (Disney Dreamlight Valley after
an update, Warhammer 40,000: Regicide), and Grounded 2 from 0.5.0.2 on loops at its login screen —
with SteamAutoCrack too, so that one is the game, not the tool.

---

## Two properties to know about

Neither is a reason to avoid it. Both are things you'd want to have been told.

**It fetches RUNE from the author's own mirror** (`Mush-iii/rune-emu`). RUNE has no upstream
repository at all, so this is a copy of a copy — the provenance problem from
[the RUNE guide](RUNE%20Steam%20Emulator%20User%20Guide.md#whats-actually-in-the-package), one step
further removed. It does not use gbe_fork at any point.

**It updates itself** by downloading `Updater.exe` from a *branch* rather than a release, so there's
no version and no hash to compare — what you get is whatever that branch holds on the day. You can
turn this off: `CheckUpdatesOnStartup` in its settings.

---

## Undoing it

On a copy, delete the copy. On a real Steam install, the fastest route is Steam's own repair:
**right-click the game → Properties → Installed Files → Verify integrity of game files.** A few
minutes, and no full re-download.

By hand, in Regular mode: delete RUNE's `steam_api64.dll` and `steam_emu.ini`, rename
`steam_api64.rne` back to `steam_api64.dll`. If Steamless rewrote the executable, restore your
backup of it too.

---

## Links

- Repository: <https://github.com/Mush-iii/RUNEAutoCracker> (BSD-3-Clause)
- The emulator it installs: [RUNE guide](RUNE%20Steam%20Emulator%20User%20Guide.md)
- The one to try first: [gbe_fork](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)
- Why any of this needs checking: [Closed-source tools](../other/Closed-Source%20Tools.md)
