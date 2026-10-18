# Goldberg Steam Emulator (gbe_fork) — Installation Guide

Configure the Goldberg Steam Emulator fork so a game you own runs without the Steam client.

> **For legal owners only.** This does not unlock games you haven't bought.

---

## What you need

| Item | Where |
|---|---|
| gbe_fork release — `emu-win-release-vs22.7z` (or `-vs26`, see below) | https://github.com/Detanup01/gbe_fork/releases |
| The game's AppID | https://steamdb.info/ |
| *(optional)* config generator, for achievements and DLC | [GSE-Generator](https://github.com/brunolee-GIT/GSE-Generator), or the maintained `generate_emu_config_old` in [gse_fork_tools](https://github.com/alex47exe/gse_fork_tools) — [see the trade-offs](../game-files/Saves%20and%20Achievements.md#achievements-two-halves-that-people-confuse) |

> **You don't have to do this by hand.**
> [SteamAutoCrack](#the-automated-route) runs all six steps below in one pass and generates the
> config too. It's the faster answer for most games — the manual route is here because it's the one
> that teaches you where things live, and the one you'll need when the automatic one goes wrong.

> **Two builds per release.** Since `release-2026_09_16`, upstream ships every Windows archive twice:
> `emu-win-release-vs22.7z` and `emu-win-release-vs26.7z` — same source, Visual Studio 2022 or 2026.
> Same layout, no runtime to install for either. Take **vs22** (it's the one
> verified here,
> renamed there to `emu-win-release.7z`); try vs26 if a game misbehaves. Older releases have a single
> `emu-win-release.7z`, which is what the rest of this guide calls it.

Throughout this guide, **game folder** means the directory containing the game executable.
For Unreal Engine titles that is usually `…\<Game>\Binaries\Win64\`, not the root folder.

> **64-bit vs 32-bit:** this guide uses the 64-bit names (`steam_api64.dll`, `x64` folders).
> For a 32-bit game, substitute `steam_api.dll` and the `x86` folders everywhere.

---

## Step 1 — Extract the release

The release is a `.7z`, so you need [7-Zip](https://www.7-zip.org/) — Windows Explorer won't open
it. Since May 2026 each release comes as two Windows builds: **vs26** needs Windows 10 or later,
**vs22** still runs on Windows 7 (the maintainer's words); this repo pins vs22. On Windows 7 it asks
for `XINPUT1_4.dll`, which only exists from Windows 8 — a copy of `xinput1_3.dll` renamed to that, next
to the game, is the reported workaround. Extract it to a temporary folder; everything lands under a `release\` directory. You'll use
three things from it:

- `release\regular\x64\steam_api64.dll` — the emulator DLL
- `release\steam_settings.EXAMPLE\` — the configuration folder template
- `release\tools\generate_interfaces\` — the interface generator

The other two folders are different tools, not fallbacks, and neither is covered here:

- `experimental\` — the same emulator plus a filter that **blocks every connection to a non-LAN
  address** (upstream's answer to games that phone analytics services), the ability to load extra
  DLLs — and **the overlay**, which only exists in this build. Note what the filter costs:
  `custom_broadcasts.txt` to internet addresses only works once `disable_lan_only=1` is set, and a
  game that needs its own server for something (a server-side DLC check) loses it.
- `steamclient_experimental\` — an injector-based setup that impersonates Steam's backend instead of
  this DLL. Out of scope for these notes.

---

## Step 2 — Back up the original DLL (do this first)

In the game folder, rename the existing `steam_api64.dll` to **`steam_api64_o.dll`**.

> **This is not optional.** Step 4 needs the *original* Steam DLL to work. If you overwrite it
> with the emulator DLL now, you'll have to re-download the game files to get it back.

**Which `steam_api64.dll`?** Search the whole game folder for it before touching anything. In a
packaged **Unreal Engine** game it usually isn't next to the exe at all: the engine loads it by
explicit path from

```text
<game folder>\Engine\Binaries\ThirdParty\Steamworks\Steamv1xx\Win64\steam_api64.dll
```

(`Steamv157`, `Steamv161`… depending on the build), often with its own `steam_appid.txt` beside it.
Replacing a copy next to the exe there does nothing — the game keeps loading Valve's. The DLL to
back up and replace, and the folder that gets `steam_settings\`, is the one in that path. **Unity**
games keep theirs in `<Game>_Data\Plugins\x86_64\` (or `Plugins\`). And check the DLL's actual
bitness rather than its name — some 64-bit games ship a 64-bit file called `steam_api.dll`.

**Lost the original?** Re-downloading the game is one way. The other is Valve itself: every
`steam_api(64).dll` version ships inside a **Steamworks SDK**, and
[partner.steamgames.com/downloads/list](https://partner.steamgames.com/downloads/list) lets any Steam
account log in and download old SDKs. Match the version the game shipped with (right-click the DLL →
*Properties* → *Details* → *File version*; SDK 1.59 = 8.63.11.84, 1.60 = 8.97.99.70, 1.61 = 9.31.86.4,
1.62 = 9.60.44.10), and check the file carries a valid **Valve Corporation** signature (*Digital
Signatures* tab). That beats any "collection of original DLLs" from a forum: it's the same file, from
the only source that can't have been tampered with. One caveat — a few games ship a
developer-modified build with a hash of its own (the Indiana Jones updates are an example), so for
those the game's own files are the only true original.

---

## Step 3 — Install the emulator DLL

Copy `release\regular\x64\steam_api64.dll` from the extracted archive into the game folder.

Your game folder now has both `steam_api64.dll` (Goldberg) and `steam_api64_o.dll` (original).

> If your antivirus deletes the file, add the game folder to its exclusions and copy it again.

---

## Step 4 — Generate `steam_interfaces.txt`

Goldberg needs to know which Steam API interface versions the game was built against. That
information lives in the **original** DLL.

1. Open `release\tools\generate_interfaces\` in the extracted archive.
2. Drag **`steam_api64_o.dll`** (the backup from step 2) onto `generate_interfaces_x64.exe`.
3. A `steam_interfaces.txt` appears next to the tool.

> **Common mistake:** dragging Goldberg's own `steam_api64.dll` onto the generator. It produces a
> file, but the interface versions are the emulator's, not the game's — and the game will
> silently fail to start. Always use the original DLL. Upstream's own note on the tool says the
> same thing in bold.
>
> The generator takes any path (`generate_interfaces_x64.exe <path to the dll>`), so the renamed
> backup is not a problem — no need to rename anything back.

---

## Step 5 — Create the `steam_settings` folder

1. Create a folder named **`steam_settings`** in the game folder.
2. Move the `steam_interfaces.txt` from step 4 into it.
3. Create `steam_settings\steam_appid.txt` containing **only** the numeric AppID — no spaces,
   no label, no trailing text.

Those two files are the whole requirement; the emulator runs on defaults for everything else.
`release\steam_settings.EXAMPLE\` is a template to take *individual* files from when you need them
— see [Common configuration](#common-configuration). Copying the whole folder in is fine too
(upstream suggests it), just noisier.

> **The example files keep working under their own name only after you rename them.**
> `configs.user.EXAMPLE.ini` is inert; `configs.user.ini` is read. This catches people who copy the
> template folder wholesale, change a value, and wonder why nothing happens.

> **Watch the extension.** Windows hides it by default, so `steam_appid.txt` is easily created as
> `steam_appid.txt.txt`. Enable *View → Show → File name extensions* in Explorer and check.
>
> The emulator looks for the AppID in three places, in order: `steam_settings\steam_appid.txt`,
> then the game's working directory, then next to the Steam API DLL. Upstream recommends the first,
> which is what this guide does — if a game still doesn't pick it up, dropping a copy next to the
> executable covers the second.

---

## Step 6 — Verify the layout

```text
<game folder>\
├── Game.exe
├── steam_api64.dll             ← Goldberg
├── steam_api64_o.dll           ← original, keep it
└── steam_settings\
    ├── steam_appid.txt         ← AppID only
    └── steam_interfaces.txt    ← generated from the ORIGINAL dll
```

---

## Launching

Run the game executable directly. If the game shipped with a `.bat` / `.cmd` launcher, use that
instead — it may set required environment variables.

**Some games expect the arguments Steam adds when it launches them** and misbehave without them —
Source games want `-game <folder> -steam`, Days Gone `-Steamworks -Installed`. They're listed on the
game's SteamDB page, *Configuration* tab → launch options; put them in a shortcut's *Target* line
(or `ExeCommandLine` if you use the steamclient loader).

The game should start with the Steam client closed.

---

## Troubleshooting

### The game doesn't launch

- On Unreal Engine games, check you replaced the DLL under `Engine\Binaries\ThirdParty\Steamworks\`
  (see [step 2](#step-2--back-up-the-original-dll-do-this-first)), not one next to the exe.
- `steam_settings\` must sit **beside the emulator DLL** (upstream's wording) — usually that's next to
  the executable, not the game's root folder; on Unreal it's the `ThirdParty\Steamworks\…\Win64` folder.
- `steam_appid.txt` must contain the AppID and nothing else.
- `steam_interfaces.txt` must exist and be non-empty (0 KB means step 4 failed).
- Confirm you actually replaced `steam_api64.dll`, and that you generated the interfaces from the
  **original** DLL, not Goldberg's.
- **The real Steam starts, the store page opens, or you get *"Application load error 3:0000065432"*:**
  the exe is wrapped in SteamStub and is calling Steam itself — [Steamless](Steamless%20Usage%20Guide.md).
- **No `GSE Saves` folder ever appears** (it's created on the first achievement or save write): the
  game may not be loading your DLL at all — you replaced the wrong copy.

### The game crashes on startup

- Verify the game files through Steam first, to rule out a corrupted install.
- If it still won't start, the executable is probably wrapped in SteamStub →
  see the [Steamless guide](Steamless%20Usage%20Guide.md).
- With `debug` builds, read the log: the DLL loads but **no Steam function is ever called** → the exe
  is wrapped (SteamStub or another DRM), not misconfigured. A line reporting `EMU_MISSING_INTERFACE`
  means the game was built with a newer Steamworks SDK than your gbe_fork knows — update gbe_fork.
- Some games crash when an optional file they rely on is absent — the known cases are an empty
  `steam_settings\leaderboards.txt` (Roof Rage, Million Arthur) and a `stats.json` whose stat
  **types** match the game's (an `int` stat declared as `float` crashes The Showdown Effect).
- **Achievement names made only of digits** get written by generators as JSON *numbers*, and the
  emulator crashes reading them — quote them as strings in `achievements.json`.
- **Source and GoldSrc games** can fail with *"STEAM certificate length error"* or refuse to load maps:
  set `new_app_ticket=0` and `gc_token=0` in `configs.main.ini`. Both default to 1, which is what games
  that pass tickets to web services (and EOS logins) need — the old engines choke on it. Source games
  may also want `215=Source SDK Base 2006` in the DLC list.
- A game that runs at 1 fps or stutters under the emulator, fine on Steam, usually spins on Steam's
  callback function without ever yielding — an emulator-side problem to report upstream, not a
  setting you're missing.

> `experimental\x64\` is **not** a fallback for crashes, despite what the folder name suggests — it's
> the build that blocks non-LAN traffic. Swapping to it to fix a crash mostly changes which thing is
> broken.

### The game says it's a pirated copy

Not a crash and not a configuration mistake: the game started, ran, and decided. Two of gbe_fork's
defaults are the usual reason, and both are the same trick — **the game asks about something that
doesn't exist, and the emulator says yes.**

| The game asks | gbe_fork's default | The lever |
|---|---|---|
| "do I own DLC *X*?" | yes, for any ID (`unlock_all=1`) | `configs.app.ini`, [see below](#dlc) |
| "is app *X* installed?" | **yes, for any ID** | `steam_settings\installed_app_ids.txt` |

The second one isn't in most guides. With no `installed_app_ids.txt`, the emulator allows the current
game, app ID 0, **and anything else**. Create the file and list only the real IDs — the game and its
genuine DLC, one per line — and every other probe gets a no:

```text
2198150
3226080
```

Both are cheap to set and worth setting together, because a game that uses one trick often uses both.

A third family of checks looks at the **file**, not the answers: the game hashes or measures
`steam_api64.dll` and refuses a replaced one (Koei Tecmo's Atelier and Blue Reflection games, Hitman 3
are the usual examples). [Steam-API-Check-Bypass](https://github.com/SteamAutoCracks/Steam-API-Check-Bypass)
(same authors as SteamAutoCrack, public source, no licence file, v2.3) intercepts the game's file
reads and hands it the original you kept — out of the box it looks for `steam_api64_o.dll` (this
guide's name), `.org` and `.dll.bak`; a `SteamAPICheckBypass.json` handles anything else. Load it as
`version.dll` (or `winmm.dll` / `winhttp.dll`) next to the exe; users also drop it into gbe_fork's
`steam_settings\load_dlls\`. SteamAutoCrack can apply it for you. It does nothing against kernel anti-cheat or checks done on a server.

#### When neither works — a real case

**Tiny Glade** (AppID 2198150), tested 2026-08-10 against gbe_fork `release-2026_07_19`, installed by
hand. The base was sound: interfaces generated from the original DLL (29 of them), correct AppID, and
the game launched with the Steam client closed. Then:

- `unlock_all=0` with its one real DLC listed → the accusation came back
- `installed_app_ids.txt` limited to the two real IDs → still came back

**The check is delayed by several minutes.** That's the part worth carrying away, and it's clearly
deliberate: the game runs, you conclude it worked, you put your tools away, and the message arrives
later. Time your test from launch and wait before declaring victory — on anything, not just this game.

The cause was never established, because the investigation was stopped rather than finished. What
would have settled it is in the next section. Treat this as "the two documented levers are not
exhaustive", not as "Tiny Glade is unbeatable".

### Reading what the game actually asks

Guessing which check a game performs is expensive — three wrong guesses cost more than one
measurement. There is a way to look.

Upstream publishes a **debug build** on the same release page, `emu-win-debug.7z` (~78 MB). It is the
same emulator with logging compiled in: every call the game makes is written, by name
(`Steam_Apps::…`, `Steam_User::…`), to **`STEAM_LOG.txt`** beside the DLL.

1. Rename your working `steam_api64.dll` out of the way — you'll put it back
2. Copy the debug build's `release\regular\x64\steam_api64.dll` in its place
3. Leave `steam_settings\` exactly as it is, so you measure the setup that fails
4. Run, reproduce the problem, quit, and read the last lines of `STEAM_LOG.txt`

The last calls before the game changed its behaviour name the question it asked. Then swap the
release build back: the debug one logs constantly and is not something to play on.

If the log shows nothing unusual, that is also an answer — the check isn't going through the Steam
API at all, and there is nothing in `steam_settings\` that will change it.

### Antivirus keeps deleting the DLL

Add the whole game folder to the exclusion list, then re-extract the release and copy the DLL
again. Every emulator DLL of this kind trips heuristic detection.

---

## Saves

By default:

```text
C:\Users\<YourUsername>\AppData\Roaming\GSE Saves\
```

Some games write to their own save location regardless. Which of the two you're in — and how to move
your existing Steam saves across before you switch — is
[Saves & achievements](../game-files/Saves%20and%20Achievements.md).

To keep saves inside the game folder, edit `steam_settings\configs.user.ini` — the file you get by
copying `configs.user.EXAMPLE.ini` and dropping the `.EXAMPLE` (step 5):

```ini
[user::saves]
local_save_path=./
```

`./` means the folder of the emulator's DLL, which isn't always the game's root (Unity:
`<Game>_Data\Plugins\x86_64\`). Pin `account_steamid` at the same time, or a game that files saves by
SteamID may start blank — details in
[Keeping the saves next to the game](../game-files/Saves%20and%20Achievements.md#keeping-the-saves-next-to-the-game).

> Key and section names have changed between gbe_fork versions — open the
> `configs.user.EXAMPLE.ini` shipped in your release and match what's already commented in it
> rather than pasting blindly.

---

## Common configuration

Three things people almost always want, and where they actually live. All of these are files you
create by copying the matching `*.EXAMPLE.ini` from the release and dropping the `.EXAMPLE`, as in
step 5 — set only the keys you care about, leave the rest out.

### Player name

`steam_settings\configs.user.ini`:

```ini
[user::general]
account_name=YourName
language=english
```

The default is `gse orca`, which is what everyone in your LAN lobby will see until you change it.
`language` must match a name in the release's `supported_languages.txt` or it's ignored.

### DLC

**There is usually nothing to do.** `unlock_all` defaults to **1**, so the emulator already reports
every DLC as owned — which is why a game run through gbe_fork shows its DLC content without any
config file at all. Confirmed in the wild on Car Mechanic Simulator 2018.

The config exists for the **opposite** case: **some games detect emulators by asking about a DLC that
doesn't exist**, and answering "yes, you own it" gives them away. If a game misbehaves, set
`unlock_all=0` in `steam_settings\configs.app.ini` and list the real ones instead, one `ID=name`
per line:

```ini
[app::dlcs]
unlock_all=0
123456=Soundtrack
234567=Season Pass
```

Note that this is the emulator's own answer, and has nothing to do with whether the DLC *files* are
on disk — see [DLC Unlocking](../other/DLC%20Unlocking.md) for that distinction. *A Dance of Fire and
Ice* is the clear example: its Neo Cosmos DLC reports owned under gbe_fork either way, but its levels
only open once the DLC's two `Bundles\neocosmos_*.bundle` files are in the copy — files Steam only
downloads for owners. Copy your install from a Steam library where the DLC is installed.

Its sibling is `steam_settings\installed_app_ids.txt`, which does the same job for *"is this app
installed"* rather than *"do I own this DLC"*. Both are covered together under
[the game says it's a pirated copy](#the-game-says-its-a-pirated-copy).

DLC IDs come from the game's SteamDB page, under *Depots* / *DLC*.

Leave out DLC that only exist as keys or as content you'd have to download (owners-only packages,
CD-key DLC): listing those has crashed games. The list can bite the other way too: **Shadow of the Tomb Raider crashes with any list**, even an
empty one, and **A Plague Tale: Requiem crashed on *New Game* with a list** but not without. If a game
gets worse after you add one, go back to `unlock_all=1`. Two related files: a game that switches to the
wrong language needs `steam_settings\supported_languages.txt` to include the language you chose, and
some games read their language or content from installed *depots* — `steam_settings\depots.txt`.

This only applies while you're running the game through the emulator. If you'd rather stay on the
real Steam client and just unlock DLC, that's a different tool —
[DLC Unlocking](../other/DLC%20Unlocking.md).

### Overlay

Off by default, and **only in the experimental build** (`release\experimental\x64\steam_api64.dll`
instead of `regular\`) — the regular DLL ignores the setting. Then `steam_settings\configs.overlay.ini`:

```ini
[overlay::general]
enable_experimental_overlay=1
```

It's called experimental for a reason — it hooks the renderer, so it can cost frames or break the
game outright. Turn it on only if you need the in-game friends list or achievement notifications,
and turn it back off at the first sign of trouble.

What breaks it in practice: other overlays (RivaTuner/Afterburner — set RTSS's detection to skip the
game, Special K, Epic's own EOS overlay) and DX12 games that create their renderer late, which
`hook_delay_sec` (3–20) in the same file works around. And if you see **Steam's real overlay** in the
game, it loaded Valve's `GameOverlayRenderer` from your Steam folder — your setup isn't the one being
used.

---

## The automated route

[SteamAutoCrack](https://github.com/SteamAutoCracks/Steam-auto-crack) (MIT, actively developed —
v3.5.1.0 as of 2026-10-10) does every step on this page in one pass: it unpacks SteamStub, installs
gbe_fork, and generates the emulator's configuration. It isn't a rival method — it drives
**Steamless** and **gbe_fork**, the same two tools documented here, plus its own
Steam-API-Check-Bypass. All three are listed as its dependencies. Since 3.5.1.0 the Steamless it
embeds is the [Steamless-KR](https://github.com/K0oRui/Steamless-KR) fork rather than atom0s'
release — same licence, public source, see the
upstream release notes.

The step-by-step, and what to set, is in
[the generic guide](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#4-apply-goldberg).
Its readme states **.NET 10**; if it refuses to start, that's the Desktop Runtime to install — the
**x86** one: the app is built 32-bit (`<Platforms>x86</Platforms>`), and users with only the x64
runtime found it "not installed".

Two more things the release thread taught:

- **Searching a game by name needs a Steam Web API key** since Valve retired the keyless app list in
  November 2025: the tool now calls `IStoreService/GetAppList`, which wants one, and logs *"Steam Web
  API Key / Access Token not set"* otherwise. Get a key at
  [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey), or type the AppID yourself.
  The settings also accept an *access token* instead — don't: that's a login session, not an API key.
- **Mind the name.** *Steam Auto Cracker* (BigBoiCJ, Python) is a different, older tool — it installs
  the ALI213 emulator by default and CreamAPI, and its author announced in October 2026 that he's no
  longer maintaining it. Everything here means SteamAutoCrack from the `SteamAutoCracks` organisation
  (GitLab mirror: `gitlab.com/steamautocracks/Steam-auto-crack`, used when the GitHub org was briefly
  unreachable in April 2026).

**Where it genuinely saves you an evening** is the part this guide is quietest about: generating the
game info. It queries Steam for the DLC list and writes `configs.app.ini` with `unlock_all=0` and the
real IDs enumerated — which is exactly the configuration
[the anti-emulator check section](#the-game-says-its-a-pirated-copy) tells you to build by hand, and
which by hand means collecting IDs from SteamDB one at a time. Same for `achievements.json`, the file
[Saves & achievements](../game-files/Saves%20and%20Achievements.md) sends you to a third-party
generator for.

Three things to know before you use it:

- **The gbe_fork build isn't one you chose.** It ships its own copy and updates it on its own
  schedule, so the DLL landing in your game folder is not the one whose hash you verified. If that
  matters — and for anything involving EOS it does — install gbe_fork yourself over the top afterwards.
- **It writes `.bak`, not `_o`.** Same file, its own suffix. Keep it either way.
- **It has a Restore Crack function**, which undoes everything it did. Worth knowing before you start
  unpicking things by hand.

---

## What works and what doesn't

| | |
|---|---|
| Offline play | ✅ |
| LAN multiplayer | ✅ (over the internet: virtual LAN, or `custom_broadcasts.txt` — see below) |
| Official Steam online multiplayer | ❌ |
| Steam overlay, friends, cloud | ~ emulated locally — the overlay is off by default, see [Common configuration](#overlay) |
| Multiplayer that runs on Epic (EOS) | ✅ with a second layer — see the [EOS Proxy guide](../multiplayer/EOS%20Proxy%20Usage%20Guide.md) |
| Voice chat | ❌ — use Discord/Mumble |
| Controller | ✅ XInput; Steam Input games need a config generated from the game's controller VDF; actions that emulate keyboard/mouse don't work |
| `offline=1` | ⚠ breaks achievements in some games (Half-Life 2, Portal, God of War) — leave it off unless a game needs it |

That last row is worth knowing before you conclude a game's multiplayer is dead: an
`EOSSDK-Win64-Shipping.dll` in the game folder means the netcode may never have gone through Steam at
all, and gbe_fork is specifically the Steam layer that pairs best with the EOS proxy. Check the store
page first, though — that DLL also ships in single-player games for save sync and achievements, so
its presence alone proves nothing.

**Playing with someone outside your network** doesn't strictly need a VPN. Copy
`custom_broadcasts.EXAMPLE.txt` to `steam_settings\custom_broadcasts.txt` and put one address per
line — IPv4 or a hostname, the shipped example uses both. The emulator sends its discovery packets
to those addresses on top of the local broadcast. Everyone needs the other side's public IP and the
game's UDP port forwarded, which is exactly the friction a virtual LAN saves you; pick whichever you
find less annoying.

This is a fork of the original Goldberg emulator; behaviour on edge-case titles varies. In this
repo "Goldberg" always means **gbe_fork** — the original
[Mr_Goldberg emulator](https://gitlab.com/Mr_Goldberg/goldberg_emulator) has been unmaintained
since 2022 and is not what these guides describe.

How it got here, from the release thread: Mr_Goldberg stepped back in October 2022 because repacks
and crack releases carrying his name made him look like a piracy group; the community builds that
followed became `otavepto/gbe_fork` in December 2023; when that repository was archived in June
2024, **Detanup01** — already a contributor — carried it on, and his repository is the one of record.
alex47exe's `gse_fork` is a legitimate sibling (mainly its config generator). Everything else you'll
be handed — "backup" builds on file hosts, "Best of GSE" packs, DLLs patched for one game — isn't
gbe_fork, whatever it's called. And expect a handful of antivirus hits on genuine releases: upstream's
README says the Windows build is signed with a randomly generated fake certificate on purpose, to pass
games' naive signature checks — and that you must **never install that certificate** into Windows'
certificate store.

---

## Links

- Repository: https://github.com/Detanup01/gbe_fork
- Release documentation: https://github.com/Detanup01/gbe_fork/blob/dev/post_build/README.release.md
- AppID lookup: https://steamdb.info/
