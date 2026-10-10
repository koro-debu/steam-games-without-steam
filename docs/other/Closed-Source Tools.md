# What's Not In This Repo, and Why

Sooner or later a forum thread tells you the answer is CreamAPI, or GreenLuma, or SteamTools, or
Online-Fix. None of them is here. This page states the reason once so the other guides don't have to.

The reason is **two rules, not one** — and nearly every argument about this page comes from someone
passing one of them and assuming that settles it. It doesn't. A tool has to pass both.

---

## Rule 1 — Whose licence does it need?

**Everything here works on a licence you already hold.** The tools answer, fake or bypass the
questions a game asks *around* files you own: gbe_fork replies instead of Steam, Steamless unwraps an
executable you have, SmokeAPI answers DLC ownership on a game in your library, DepotDownloader asks
Valve for depots **your account** is entitled to.

A tool fails this rule when it needs a licence that isn't yours — most often somebody else's, lifted
and redistributed. That's [a different activity](#where-the-manifests-actually-come-from), and it's
the line this repo doesn't cross. Not a moral position: it's a scope, and the whole repo is built on
one side of it.

The clean test: **remove every file the tool touches. Does what's left still require you to have
bought the game?** If yes, it's in scope. If the game runs for someone who never bought it, it isn't.

## Rule 2 — Can you find out what it does?

A tool passes when either of these holds:

1. **The source is readable** — gbe_fork, Steamless, SmokeAPI, eos-proxy, DepotDownloader,
   uc-online2. You can see what it does, and so can anyone you'd ask.
2. **The binary can be characterised** — you can hash it, compare it against an upstream release,
   read its sections, imports and signature, and **write down what you found, including when you
   found nothing.** The [Releases tab](../index.md#verifying-what-you-download) pins the exact
   copies these guides were written against.

The second condition is why [RUNE](../running/RUNE%20Steam%20Emulator%20User%20Guide.md) and
TENOKE are here despite
having no source and no upstream: both were opened up and described, and both release pages say
plainly where the description ran out. RUNE's DLL is packed, so static analysis yields nothing and
its page says so; TENOKE's isn't, so there's more to report and less to trust on reputation alone.

What fails this rule is a binary built to defeat the examination — obfuscated, single-source, no
upstream — because then "it came back clean" is not a finding, it's an absence of one.

### The two rules are independent

This is the part that was implicit before and caused the confusion:

| | Passes Rule 1 (scope) | Fails Rule 1 |
|---|---|---|
| **Passes Rule 2 (audit)** | in the repo | **SteamTools, LuaTools, Arachnel** — open source and excluded |
| **Fails Rule 2** | RUNE, TENOKE — admitted, with the gap documented | CreamAPI, Online-Fix |

"But it's open source" answers Rule 2 and says nothing about Rule 1. That's the whole content of the
top-right cell, and it's where most of the popular tools sit.

---

## Readable is not the same as freely licensed

Worth separating, because they get conflated. Rule 2 is about **auditing** — can you find out what it
does. What you're allowed to *do* with it afterwards is a different question, and the answers vary
more than you'd expect (checked 2026-08-09; gse_fork_tools and Achievement Watcher Next 2026-10-10):

| Tool | Licence |
|---|---|
| gbe_fork | LGPL-3.0 |
| DepotDownloader | GPL-2.0 |
| SmokeAPI, Koaloader | Unlicense — public domain |
| SAM | zlib |
| GSE-Generator | MIT |
| gse_fork_tools | LGPL-3.0 |
| RUNEAutoCracker | BSD-3-Clause |
| Achievement Watcher, Achievement Watcher Next | LGPL-3.0 |
| **Steamless** | **CC BY-NC-ND 4.0** — non-commercial, and *no derivatives* |
| **eos-proxy** | **none at all.** Source is public on GitHub, but with no licence file on any branch, default copyright applies |
| **uc-online2** | Unlicense with "sell" struck out and an explicit no-selling clause |
| LuaTools | MIT — and still out, on Rule 1 |
| Arachnel | no licence file; the launcher is readable, its catalog plugins are the problem |
| RUNE, TENOKE, CreamAPI, GreenLuma, Online-Fix | no source, no licence, nothing to cite |

Two of the tools this repo recommends can be read and used but not legally redistributed or
modified — Steamless because its licence forbids derivatives, eos-proxy because it grants nothing at
all. That doesn't affect using them; it does affect forking them, shipping them in something else, or
publishing a patched build.

---

## Where the manifests actually come from

Rule 1 is abstract until you follow the chain, so here it is. This is the mechanism behind SteamTools
and everything that feeds it, and knowing it makes the boundary obvious rather than arbitrary.

**Step 1 — somebody who owns the game installs it.** Their Steam client ends up holding two things:

| What | Where | What it is |
|---|---|---|
| `.manifest` files | `Steam\depotcache\` | the file list and build snapshot of each depot |
| **depot decryption keys** | `Steam\config\config.vdf` | Valve hands your client the key for depots **your account owns** |

**Step 2 — a ripper reads both.** LuaMaker, SteamManifestRipper, Onekey and friends parse
`config.vdf`, copy the matching manifests, and emit a Lua file:

```lua
addappid(appID)
addappid(depotID, 1, "<depot decryption key>")
setManifestid(depotID, "<manifest gid>")
```

**Step 3 — it gets published.** ManifestHub is the canonical one: a git branch per AppID, each
holding the `.lua` and the `key.vdf`. Websites index them and serve ready-made ZIPs.

**Step 4 — anyone installs SteamTools and that Lua.** A DLL patches the client's ownership, package
and depot-key paths; the client believes it has a licence and downloads the game.

### The part worth understanding

**The game data comes from Valve's own CDN, and always did.** Those chunks are served to anybody who
asks — they are encrypted, and that is the entire access control. Valve gives the key to accounts
that bought the app.

So what circulates in this ecosystem **is not the game.** It's the key, extracted from the client of
someone who paid for it. The download is Valve's bandwidth; the licence is somebody else's.

That's why the boundary falls where it does, and why "the source is on GitHub and it's MIT" doesn't
move it. The tool being readable was never the issue — a redistributed decryption key is the issue,
and no licence on the front end changes what the back end is.

---

## The tools themselves

### SteamTools, and everything that manages it

**SteamTools** and its imitators — SteaMidra, SteamDaddy, and a new one most months — plus the
front-ends that have grown around them:

- **[LuaTools](https://github.com/madoiscool/LuaTools)** — MIT, C#/WPF, 350+ stars, genuinely open.
  Its own description: *"AppID Manager for ST … browses and installs manifest sources, edits
  `stplug-in` lua files (depot pinning, per-depot enable/disable), manages unlocker modes."*
  A GUI over step 4 above.
- **[Arachnel](https://github.com/BadKiko/Arachnel)** — an open-source Qt launcher with a plugin
  system. The launcher is neutral; its two reference sources are not. Its own plugin list describes
  them as *"Russian site similar to online-fix.me"* (torrent) and *"Steam direct download via Ryuu
  manifests"*, the latter marked recommended.

**They pass Rule 2 and fail Rule 1.** Nothing about their code is the problem. What they manage is.

### CreamAPI

**What it does:** the original Steam DLC unlocker — the same job as [SmokeAPI](DLC%20Unlocking.md).
It's also where the `_o` convention comes from: rename `steam_api64.dll` to `steam_api64_o.dll`, put
CreamAPI's DLL in its place, and it answers ownership questions for you.

**Why not here:** closed with no official home, circulating as forum attachments; every DLC ID listed
by hand in `cream_api.ini`; proxy mode only, so every game update wipes the install; and frozen
against a Steamworks SDK that keeps moving. SmokeAPI does the job, discovers the IDs itself, and
survives patches.

**The one case it still wins:** an old game whose cs.rin.ru thread already contains a complete,
tested `cream_api.ini`. You inherit somebody else's work instead of rebuilding it. That's a real
saving, paid for with an unverifiable binary.

### GreenLuma Reborn

**What it does:** rather than touching the game, it injects into the **Steam client itself** so that
AppIDs and DLC report as owned.

**What that is not:** a licence. The claim is made to your own client, locally; Valve's servers are
unaware of it and keep deciding what your account actually owns. Depot keys come from those servers,
which is the same wall [DepotDownloader](../game-files/DepotDownloader.md) hits with `AccessDenied` —
and the reason the ecosystem above has to redistribute keys at all. An entry appearing in your
library is not a game you can download.

**Why not here:** Rule 1 in its purest form, plus everything else in this repo operates on files in a
game folder. Remove them and nothing remains. This operates on the client you're logged into, which
moves the exposure from "a game misbehaves" to "my account's client is running modified code".

If your goal is DLC in a game you own, [SmokeAPI](DLC%20Unlocking.md) does that without going
anywhere near the client.

### Online-Fix

**What it does:** ready-made multiplayer fixes, largely for games whose netcode this repo's tools
don't cover. It works, it's popular, and it's genuinely convenient.

**Why not here:** it fails both rules. The DLLs are obfuscated and come from a single site with its
own launcher, so a clean VirusTotal score is weak evidence rather than proof — obfuscation is
precisely what defeats the static analysis those engines do. And the fixes are built for, and
distributed alongside, repacked builds.

The open equivalent in the same shape — one DLL, dropped in the game folder, real online instead of
LAN — is [uc-online2](../multiplayer/uc-online2.md), which is in the repo with its real cost stated.

#### One package, opened up — Big Walk, 2026-08-28

The argument above was theoretical until this. A real Online-Fix package was taken apart statically
on a Linux box, without ever being executed. It is the only observed case in this repo, and it is
worth reading before deciding either way, because it does **not** land where you'd expect.

**What was in it.** Seven files. `OnlineFix.url` pointing at online-fix.me, `OnlineFix.ini`,
`dlllist.txt`, three DLLs, and a `Big Walk_Data\Plugins\x86_64\` folder.

**How it installs itself** — worth knowing, because it isn't the pattern the rest of this repo uses.
It does **not** replace `steam_api64.dll`. It ships a `winmm.dll` in the game folder, which Windows
loads in preference to the real one in System32, and that proxy then loads whatever `dlllist.txt`
names:

```text
SteamOverlay64.dll
OnlineFix64.dll
```

That's arbitrary DLL injection into the game process, arranged through search-order hijacking. Less
invasive than swapping the Steam API; broader in what it can do once loaded.

**What the config says it does.** `OnlineFix.ini`, verbatim in the parts that matter:

```ini
RealAppId=1478500      ; Big Walk
FakeAppId=480          ; Spacewar
EmulateTicket=false
PhotonIntegration=false
[EOSAuthWrapper]
DeviceIdAuth=true
```

Read that against the rest of the repo. `FakeAppId=480` is
[uc-online2](../multiplayer/uc-online2.md)'s exact mechanism, down to the choice of Spacewar.
`EmulateTicket` and `PhotonIntegration` are uc-online2's option names. `DeviceIdAuth` is what
[eos-proxy](../multiplayer/EOS%20Proxy%20Usage%20Guide.md) does. **This package is those two tools in
one archive**, and both of them are here, readable, with their costs written down.

**What checked out clean:**

| File | Verdict |
|---|---|
| `steam_api64.dll` | **Valve's genuine DLL**, signed `Valve Corp., Bellevue` — 0/69, 47,166 submissions. Untouched, and shipped so you have a known-good one |
| `EOSSDK-Win64-Shipping.of` | **Epic's genuine SDK**, signed `Epic Games Inc.` — 0/70. The original, renamed as backup |
| `SteamOverlay64.dll` | unsigned, not packed (entropy 5.97), imports only `KERNEL32`/`USER32`/`ADVAPI32` — **no networking imports, no URLs, no IPs**. One export, `OnlineFix`. 3/71 on **32,516** submissions, all category labels: `RiskWare.GameHack`, `W32.Malware.Gen`, `APEX Malicious` |

**What could not be checked, and why it matters.** `OnlineFix64.dll` (13.4 MB) and `winmm.dll`
(502 KB) were unreadable — Windows Defender was denying access, and quarantined both during the
session. **Those two are the payload**: the injector and the module that does the work. The three
clean files are two signed originals and an overlay stub with no network access; they say nothing
about the other two.

**What Defender called them:**

```text
Trojan:Win/Malgent
Trojan:Win32/Kepavll!rfn
Trojan:Win32/Ravartar!rfn
```

Both readings, honestly. **Against a verdict:** the `!rfn` suffix marks Microsoft's cloud ML naming
rather than a signature, and it has a well-known false-positive rate on cracks, loaders and packed
binaries. Two of the three are that. **For one:** the prefix is `Trojan:` with a named family, not
the `PUA:` / `HackTool:` / `RiskWare` shape this repo documents as the expected noise for the
category — the shape `SteamOverlay64.dll` itself came back as, on 32,516 submissions. Those are
different classes of claim.

**Conclusion: unresolved, and that is the finding.** Nothing here proves malware. Nothing here
clears it either, because the only files that could settle it are the two that can't be read without
turning off the thing that's objecting. That is the position this page describes in the abstract, met
in practice — and it is not a position the repo's other tools ever put you in, because with them you
can look.

For this specific game the clean route existed all along: Big Walk runs on EOS, so
[eos-proxy](../multiplayer/EOS%20Proxy%20Usage%20Guide.md) does the same `DeviceIdAuth` job with
public source, a pinned hash, and 0/70. Tested since: Big Walk under gbe_fork plus eos-proxy's two install steps works
(2026-10-10).

*Nothing in the package was executed at any point, and the files were destroyed afterwards.*

---

## What looking inside them has found

People on cs.rin.ru have opened up the scene emulators over the years. Three findings are worth
knowing, because they show what "closed" means in practice — not necessarily malice, but behaviour
nobody tells you about.

- **CODEX's Steam emulator** (2023 write-up, and RUNE is its successor — [the same findings
  apply](../running/RUNE%20Steam%20Emulator%20User%20Guide.md#whats-actually-in-the-package)): UPX
  packing with the markers renamed so the standard unpacker refuses it; a fake certificate appended so
  it passes as Valve's file; `WinVerifyTrust` hooked so **every signature check in the process
  succeeds**; seven `ntdll` file and loader functions hooked to hide files and silently swap in
  renamed originals; and every function and file name stored as a truncated MD5, so even the people
  reversing it took years to decode most of the hidden filenames. Its "block network" option hooks a
  handful of socket and WinHTTP calls and lets private ranges through, plus some odd non-reserved ones
  — it's not a firewall.
- **ALI213's emulator** creates a shortcut to the ALI213 website in the game folder **every time the
  game starts** — but only when Windows' *Language for non-Unicode programs* is set to Chinese
  (Simplified). A forum member traced it in 2016 and found it in builds going back to 2013. Harmless
  in itself; the point is that it's undocumented, conditional, and targeted.
- **"SFK"**, presented in 2022 as a new emulator from a scene group, turned out on inspection to be
  **Goldberg wrapped in VMProtect** — an open-source emulator made unreadable for no reason anyone
  could name. When an open-source tool exists, an obfuscated copy of it is all cost and no benefit.

Two more names you'll be offered in 2026, both to skip. **SOVEREIGN Emulator**: closed, from a
repack group's developer, no thread of its own, unknown even to the forum regulars. **GoldbergDrop**:
its source is on GitHub, but its author describes it as entirely AI-written by a non-programmer, and
beyond setting up Goldberg it ships GreenLuma in a password-protected archive, injects it into Steam,
and offers to start itself with Windows — [Rule 1](#rule-1--whose-licence-does-it-need) territory,
whatever the Goldberg half does.

**Denuvo "activation" apps.** Tools now circulate that log into your Steam account (password,
TOTP or QR code) to fetch a Denuvo activation ticket, then turn it into a short "share code" for
someone else to paste — *Contrary: Janus* (June 2026) is the polished example: an installer with no
source in sight, a DLL injected into the game, and a "Leech" mode built for handing activations to
people who don't own the game. Anything that wants your Steam login *and* has no source is the worst
combination on this page; the open-source ticket generator gbe_fork's ecosystem uses doesn't need to
see your password at all.

---

## If you use one anyway

That's a legitimate call — sometimes nothing here covers your game, and the alternative is not
playing. Make it deliberately rather than by default:

- **Check what you're actually running.** Hash it, submit the hash to VirusTotal, read the
  *behaviour* report rather than the score — network traffic and registry persistence mean
  something; a count of generic detections doesn't. The
  [README](../index.md#verifying-what-you-download) explains how to read those results here.
- **Prefer a copy that many people have.** High submission counts and a long history are weak
  evidence, but they're evidence; a freshly uploaded file with none is worse. This is the whole
  distance between RUNE and TENOKE.
- **Keep it away from anything with anti-cheat**, and away from an account you'd miss.
- **Know what it touches.** A DLL in a game folder is deletable. Something that injects into the
  Steam client, or installs a launcher, isn't as easy to take back.
- **Be most suspicious of "fixers".** When something breaks for a lot of people at once, an `.exe`
  that promises to repair it appears within days. One seen on 2026-09-11, `manifesthub-steam-fixer.exe`
  (sha256
  `5534869dac9989d8f46b4b936eb3bbf84d1551c3b5c6dd5efbe5b299bdc3ae49`), is the textbook case: unsigned, asked for administrator rights,
  unknown to VirusTotal, served from an anonymous storage bucket — and under a real-looking repair
  routine it **copies Steam's `config.vdf` and uploads it to a Telegram bot**. Depending on your Steam
  version that file can hold session tokens, i.e. your account. The repair part may even work; that's
  what the theft hides behind. If you ran something like it: change your Steam password, *Deauthorize
  all other devices* under Steam Guard, and re-link the authenticator.
- **Test it where it can't hurt.** A throwaway Windows Sandbox costs nothing and keeps the tool away
  from your real Steam install — with one caveat that matters here: it doesn't protect an account you
  log into *inside* it. Setup and the one trap on current Windows 11 are in the
  [README](../index.md#verifying-what-you-download).

The point of this page isn't that these tools are forbidden. It's that when one of them breaks
something, you'll have no way to find out what happened — and that's worth knowing before, not after.
