# uc-online2 — Usage Guide

uc-online2 is a modified `steam_api64.dll` that makes a game report a **different AppID** — by
default Spacewar (`480`), the free test app every Steam account owns. The real Steam client stays in
charge: lobbies, matchmaking and P2P go through Steam's actual servers, under an identity every
account is entitled to.

It is a **passthrough, not an emulator.** That single fact explains everything else here — the
requirements, the failure modes, and the risk.

> **For legal owners only**, like everything else here — and the account exposure is real, and higher
> than anything else in this repo. You are running a modified DLL inside a live, logged-in Steam
> session. gbe_fork is safe in comparison precisely because it isn't on Steam at all. Never on a
> title with anti-cheat, and think twice before using an account you'd miss.

---

## When this is the right tool

Read [Multiplayer routing](Multiplayer%20Routing.md) first if you're not sure. The short version:

| Situation | Use |
|---|---|
| You want the game to run with Steam closed | [gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md), not this |
| LAN or VPN with friends is good enough | gbe_fork, not this |
| You want Steam's real matchmaking and lobbies | **uc-online2** |
| The game's session runs on Photon / PlayFab / coherence | **uc-online2** — it's the only tool here with plugins for them |
| The game's netcode is EOS | [eos-proxy](EOS%20Proxy%20Usage%20Guide.md) — you get to play with legitimate players, which this can't offer |

---

## Get it

Upstream: <https://github.com/LukeWarmSodas/uc-online2>

**Mind which repository.** The original is `UnionCrax-Team/uc-online2` — that's what eos-proxy's
documentation links to, and it sits at v1.7.0a from June 2026. Active development happens in a
**fork**, `LukeWarmSodas/uc-online2`, which went from v1.18.0 on 2026-08-09 to **v1.20.17 on
2026-09-19** — the original's author endorses the fork and sends people there. That pace is not an
exaggeration for effect; it's the reason nothing is pinned below.

Worth stating plainly: the version you want is the fork, and the fork has a fraction of the parent's
audience (48 stars against 106 in October 2026). Fewer eyes on it, and the usual consequence — you're trusting one
person's builds, or you build it yourself.

Nothing is pinned for this one, on purpose: at this release cadence a pinned
copy would be stale within days and you'd be installing something older than what the guide
describes. Take it from upstream.

**Verified for this guide** — `uc-online2-v1.18.0-release.zip`, the `x64/steam_api64.dll` inside:

```
sha256  8cb3632329d7579a52ab65c069428dfb298f593a063d9565c19627ab3e6cc095
```

1/70 on VirusTotal, a single machine-learning score, on a binary built the same day. The source is
public and it builds with `build.bat` or the included Visual Studio project, which is the better
answer if you'd rather not trust a fresh binary.

The archive holds `x64\steam_api64.dll` and `x86\steam_api.dll`, the `patch.bat` installer, a
`plugins\` folder (Photon, EOS, PlayFab, coherence, plus a few game-specific ones) and the coherence
schema tooling.

**Re-checked on 2026-10-10 against v1.20.17** — `uc-online2-v1.20.17-release.zip`, sha256
`4e7dc31b…9a06852a`, built by the repository's own GitHub Actions release workflow. The archive as a
whole scores **32/70 on VirusTotal**, and the breakdown matters more than the number:

| File | VirusTotal | What it is |
|---|---|---|
| `x64\steam_api64.dll` (`b55a7883…`) | 0/75 | the passthrough itself |
| `UCO2.Patcher.exe` | 0/75 | the GUI installer that replaced `patch.bat` in release packages |
| `plugins\overlay_proxy.dll` (`bf9f10dc…`) | **41/75** (Microsoft `Program:Win32/Wacapew.C!ml`, Kaspersky `Yephiler`) | see below |
| the other plugins | 1–5/75, all machine-learning scores | Photon, PlayFab, EOS, coherence, … |
| `tools\coherence_schema\Extract-CoherenceSchema.ps1` | 15/75 | a script that parses a Unity asset file |

`overlay_proxy.dll` is the reason. Its source is in the repository (`plugins/steam_overlay/`) and
does what the detection pattern dislikes, on purpose: it is a **renamed system-DLL proxy** —
installed as `version.dll` (Unity) or `winmm.dll` (Unreal) next to the game — that forwards every
call to the real Windows DLL, reads Steam's path from the registry and loads Valve's
`GameOverlayRenderer64.dll` before the game creates its window. The imports and exports of the
shipped binary match that source. That is a plausible heuristic hit, not a proven clean bill: the
build isn't reproducible, so "matches the source" is as far as anyone can check. If you don't need
the Steam overlay (Shift+Tab, invites), don't install it — the patcher deploys it automatically, so
remove the `version.dll`/`winmm.dll` it left next to the exe, or set `LoadOverlay=no`.

---

## Install — the easy way

**Run `UCO2.Patcher.exe` and point it at the game folder** (or drag the folder onto it) — since
v1.20.x the release ships this GUI instead of `patch.bat`, which only remains in the source tree.
Upstream labels the GUI *experimental*; the steps below are what both do. For most games that is the
entire setup. It:

- works out the engine (Unity or Unreal) and finds the real executable;
- finds where `steam_api64.dll` actually lives and installs there, backing the original up to `.bak`;
- writes `union-crax.ini` **next to the running exe** — on Unreal that is not the game folder, and an
  ini in the wrong place is silently ignored, which is exactly the kind of failure you'd never
  diagnose;
- detects Photon, EOS, PlayFab or coherence, copies the matching plugin, and asks for whatever app
  IDs that backend needs;
- deploys the overlay proxy described above.

It never invents a Photon GUID or an Epic app for you — press Enter to skip a prompt and it writes a
stub to fill in later. It also refuses to install into a 32-bit game rather than writing an x64 DLL
that can't load.

If it reports **no secondary backend**, try the game with no plugin at all: titles whose multiplayer
is purely Steam lobbies and P2P work through plain passthrough.

## Install — by hand

1. Rename the game's `steam_api64.dll` to `steam_api64_o.dll`.
2. Copy `x64\steam_api64.dll` from the release into its place.
3. Start Steam **first**, then the game from its executable.

SteamStub-wrapped executables need [Steamless](../running/Steamless%20Usage%20Guide.md) first, as
usual.

---

## Steam and the game must run at the same elevation

This is a passthrough over Steam's IPC, and that IPC is sensitive to Windows integrity levels. Get
this wrong and the game refuses to start, fails at init, or behaves as if Steam weren't running —
none of which points at the real cause.

| Steam | Game | Result |
|---|---|---|
| normal | normal | ✅ the usual setup |
| admin | admin | ✅ use this when the game needs admin |
| normal | admin | ✅ works most of the time |
| admin | normal | ❌ the game can't reach Steam |

If a game genuinely needs admin: **Exit Steam properly** (tray icon → Exit, not just closing the
window), relaunch `steam.exe` as administrator, let it sign in, then start the game.

Two traps upstream calls out: Windows silently elevates a child process when its parent is elevated,
so launching from an elevated terminal or launcher elevates the game too — and closing Steam's window
only hides it to the tray, so switching elevation without a real Exit just reattaches you to the old
instance.

---

## Configuration

`union-crax.ini`, next to the **running executable**. Without it, the AppID defaults to `480` and
plugins aren't loaded.

```ini
[Settings]
AppId=480          ; the identity the game reports
ogAppId=440        ; the real AppID, used for ticket emulation
EmulateTicket=true
PluginsFolder=plugins

[DLC]
UnlockAll=1
211=Half-Life 2: Deathmatch
```

**`AppId`** — Spacewar by default. Some games have `480` patched into their own code and need
something else; any free multiplayer AppID works. Upstream's example is `440` (Team Fortress 2),
confirmed on one game where `480` failed — treat it as the first thing to try, not a rule. A `steam_appid.txt` appears when the game runs: that's how you confirm which ID was
accepted.

**DLC comes in two flavours**, and this is why unlocking looks unreliable elsewhere. A game either
*asks* about specific IDs, or *enumerates* your list. `UnlockAll=1` answers every question without
you knowing any IDs — but it cannot invent a list, so a game that builds its DLC menu by enumeration
sees nothing unless you name the entries explicitly. IDs come from SteamDB's DLC tab.

**Other `[Settings]` keys you'll meet** (all off unless stated):

| Key | When |
|---|---|
| `PassthroughTicket=yes` | Ask Steam for a genuine ticket instead of emulating one; wins over `EmulateTicket`. It fixed sign-in loops on games with an EOS or server-side check. |
| `SDR=yes` | Steam Datagram Relay split context, needs `ogAppId`. Added for **one** game (Machine Party); the author says it causes problems elsewhere — leave it off unless a game's entry tells you otherwise. |
| `Client=017` | Pin the `SteamClient` interface version for old-SDK games. |
| `LocalSaves` | **On by default since v1.20.16** — see *Saves* below. |
| `LoadOverlay=no` | Keep Valve's overlay renderer out of the process. |
| `GetStubbedLol` | Patch SteamStub in memory instead of unpacking it. Inconsistent in practice; [Steamless](../running/Steamless%20Usage%20Guide.md) remains the reliable route. |
| `ForceOwnership` | On by default: answers ownership checks for the real AppID. |

Under `[EOS]`, `NoPresence=1` is needed by some EOS titles (StarRupture). By default the `EOS_custom`
plugin uses an Epic app **built into the DLL**, shared by everyone running it — convenient, and the
same trade-off as the coherence shortcut below. Fill the `[EOS]` fields with your own free Epic
developer app (client-policy template *peer2peer*, all features enabled) to stop depending on it.
EOS sessions are private by design: only players with the same configuration see each other.

**Everything is logged** to `%TEMP%\uc_online2.log`. That's the first place to look, always — it
reports how many hooks were installed, which DLC entries were picked up, and whether ticket
emulation is active.

---

## What it cannot fix

Upstream documents this unusually honestly, and it's the most useful part of the whole project.

A game can ask Steam for an **auth session ticket** and hand it to a server, which validates the
signature Valve produced with its private key. `EmulateTicket` builds a structurally correct ticket —
enough for a **peer** running the same tool to accept, and never enough for a server that checks
properly. That's not a bug to work around: producing a valid signature requires Valve's key.

The author verified this concretely on Farming Simulator 25 by reading the bytes a competing fix
produces: it isn't emulating anything — it ships a **genuine Valve-signed ticket belonging to someone
else's Steam account**. Worth knowing what a tool is actually doing when it succeeds where this one
can't.

Also out of reach: anything with anti-cheat, and any publisher backend. That is not theoretical —
on Rematch, launching through Easy Anti-Cheat's launcher flags the replaced `steam_api64.dll` as a
malicious file and the game refuses to start; without EAC it only runs offline. Achievement support
was asked for and is "on the radar", not implemented.

## Saves

Before v1.20.16 this was the trap most likely to cost you hours: Steam binds cloud storage to the
AppID the process **runs as**, so every game going through Spacewar wrote into the same
`Steam\userdata\<account>\480\remote\` — and games that use Steam's file API *as* their save system
(Super Battle Golf, Don't Pull Me) lost progress, or overwrote each other's identically-named files.

`LocalSaves=true` (now the default) reports Steam Cloud as disabled, so most games fall back to their
own local folder, and serves the Steam file API from `<game folder>\uco_cloud\` for those that have no
other. Whatever was already in `480\remote\` is copied there on first run, never deleted. **If you're
on an older build, update before playing anything that keeps progress** — and back up `uco_cloud\`
with the game, because it is now the only copy of those saves.

---

## Honest caveats

- **The licence is the Unlicense, amended.** Public domain, except that "sell" has been struck out
  and replaced with an emphatic no-selling clause. That amendment is why GitHub reports the licence
  as *Other* rather than recognising it — the source is public either way.
- **The coherence `SHARED` shortcut** points at a community project on a free tier: unmonitored,
  rate-limited, rotated without notice, and everyone on it sees everyone else's lobbies. Fine for
  trying something, not something to rely on.
- **The author flags his own uncertainty** on the ticket-emulation code and asks the community to
  test it. Take that as written: this part is not settled.
- **A third-party Photon relay is offered in the forum thread** (a Cloudflare worker run by the fork's
  author) for people who don't want to create their own Photon app. Same reasoning as above: create
  your own free app, as the plugin's README walks you through.
- **It moves fast.** Releases land weekly or faster; behaviour and options in this guide were read
  against v1.18.0 and re-checked against v1.20.17 and its README on 2026-10-10.

---

## Links

- Where development happens, and what this guide describes: <https://github.com/LukeWarmSodas/uc-online2>
- The original, stalled at v1.7.0a and still what eos-proxy's docs link to:
  <https://github.com/UnionCrax-Team/uc-online2>
- AppIDs and DLC IDs: <https://steamdb.info/>
