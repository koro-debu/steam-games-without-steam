# DLC Unlocking — SmokeAPI

Every other guide here answers "how do I run this game without Steam". This one answers a different
question: **the game is installed and Steam is running normally, but its DLC is locked.**

[SmokeAPI](https://github.com/acidicoala/SmokeAPI) emulates DLC ownership at the Steamworks level and
leaves the rest of Steam alone — so multiplayer, achievements, cloud saves and the overlay keep
working, because you're still on a real Steam session. That's the whole point of it, and what makes
it a different tool from the emulators.

> **For legal owners only**, and the risk here is not the same as elsewhere in this repo. Upstream
> says it plainly: using it breaks one or more terms of service and can cost you the account. Never
> on a game with anti-cheat, never on anything competitive.

---

## Do you want this or gbe_fork?

They solve the same symptom from opposite ends. Pick one — **do not stack them**, they both want to
be `steam_api64.dll`.

| | [gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) | SmokeAPI |
|---|---|---|
| Steam client | not needed, that's the point | required, running and logged in |
| DLC | `unlock_all` in `configs.app.ini` | its whole purpose |
| Multiplayer | LAN only | real Steam, unchanged |
| Achievements | emulated locally | real, on your account |
| Ban risk | you're off Steam entirely | you're on Steam with a modified DLL |

Short version: if you're already running the game through the emulator, you have DLC handling
already — use `unlock_all`. SmokeAPI is for when you want to stay on real Steam.

---

## Is this game even a candidate?

Four checks, two minutes, before you touch a single file. A game that fails any one of them is not a
SmokeAPI case at all, and no amount of reinstalling will change that.

### 1. Does Steam declare third-party DRM or a third-party account?

Steam publishes both, and you can read them without opening a browser:

```bash
curl -s "https://store.steampowered.com/api/appdetails?appids=<APPID>&l=english&cc=us" \
  | grep -o '"drm_notice[^,]*\|"ext_user_account_notice[^,]*\|"is_free":[a-z]*'
```

`l=english&cc=us` is not optional — without it Steam localises `drm_notice` to your IP, and a French
or Turkish notice won't match the "EA / Ubisoft" keywords you're scanning for.

- **`drm_notice`** — anything mentioning EA, Ubisoft Connect, Rockstar, a launcher: stop here. The
  ownership check isn't Steamworks' to answer, so there's nothing to emulate.
- **`ext_user_account_notice`** — a required publisher account means the entitlements live on their
  servers.
- **`is_free: true`** — free-to-play. Entitlements are server-side; a client-side unlocker has
  nothing to fool.

Nothing printed at all is the good outcome.

### 2. Is there a Steam API DLL in the game folder?

No `steam_api.dll` or `steam_api64.dll` anywhere in the install directory means the game doesn't use
Steamworks for this, and SmokeAPI has nothing to attach to. Not a candidate, no exceptions.

### 3. Single-player, and no anti-cheat?

Anti-cheat inspects tampered DLLs. This is the one that costs accounts, not the one that wastes an
evening.

### 4. Is the DLC content actually installed?

Unlocking says *"you own this"*; it downloads nothing. Games that ship DLC assets with the base
install will work. Games that only fetch them after purchase will show you an unlocked entry with
nothing behind it.

You don't have to guess. Steam marks content it should only download for owners, and that's
readable — but in **two places**, and checking only the first one is a mistake this page used to make:

- depots of the **base game** that carry a `dlcappid` (ETS2's map packs);
- depots declared under the **DLC's own app ID**. The base game then shows zero gated depots, and the
  content still isn't on your disk ([A Dance of Fire and Ice](#a-dance-of-fire-and-ice-withdrawn)).

This checks both, one request per DLC (so it's slow on a game with a hundred of them):

```bash
APPID=282800   # 100% Orange Juice, as an example
APPID=$APPID python3 -c "
import json,os,urllib.request
def info(a): return json.load(urllib.request.urlopen(f'https://api.steamcmd.net/v1/info/{a}'))['data'][str(a)]
d=info(os.environ['APPID']); dep=d.get('depots',{}); ids=[k for k in dep if k.isdigit()]
gated=[k for k in ids if dep[k].get('dlcappid') or (dep[k].get('config') or {}).get('dlcappid')]
print(f'base game: {len(gated)} of {len(ids)} depots are DLC-gated')
for x in [x for x in str(d.get('extended',{}).get('listofdlc','')).split(',') if x]:
    sub=info(x); own=[k for k in sub.get('depots',{}) if k.isdigit()]
    print(f'DLC {x} ({sub.get(\"common\",{}).get(\"name\",\"?\")}): ' + (f'{len(own)} depots of its own' if own else 'no depot of its own'))"
```

**Zero gated depots and every DLC printing *no depot of its own* is the ideal case**: everything
ships in the base install and only an ownership flag stands in the way. 100% Orange Juice is that
case (0 of 6, and none of its DLC has a depot). The opposite results are
[ETS2](#a-second-one-euro-truck-simulator-2), where 111 of 115 depots are gated, and A Dance of Fire
and Ice, whose one content DLC has 4 depots of its own — either way, the content is simply not on
your disk.

### A worked example: The Sims 4

The obvious thing to try, and the textbook rejection — it fails three of the four:

| Check | What Steam returns |
|---|---|
| `drm_notice` | *"EA online activation and EA app software installation and background use required"* |
| `ext_user_account_notice` | *"EA Account"* |
| `is_free` | `true` |

Its 113 packs are EA entitlements. Steamworks never sees the question, so neither does SmokeAPI.
Any game carrying a publisher launcher lands in the same place.

### A second one: Euro Truck Simulator 2

More interesting, because it passes the paperwork and still isn't a good test. No `drm_notice`, no
publisher account, not free-to-play, SCS Software, no anti-cheat — the API check prints only
`"is_free":false`, which is the clean result.

It's check 4 that catches it. ETS2 declares 115 depots, and **111 of them are gated behind a
`dlcappid`** — meaning Steam downloads that content only for people who own the corresponding DLC.
The map expansions live in their own `dlc_*.scs` archives in the game root, and they are simply not
on your disk otherwise.

So SmokeAPI would do its job — flip the ownership answer — and you'd get an unlocked entry with no
map behind it. Look in the game folder first: the `dlc_*.scs` files you have are the DLC you can
expect to do anything with.

Two more reasons not to make ETS2 your first test: official **Convoy** sessions expect participants
to have the same map content, and **TruckersMP** is third-party, with its own account and its own
file checks. Neither is somewhere to find out.

### So what makes a good test

An independent title with a DLC or two, no launcher, no anti-cheat, and — the part everyone
forgets — DLC content that ships inside the base install. Then the result is unambiguous: it either
appears or it doesn't, and you learn something either way.

---

## Install

The release zip ([v4.1.3](https://github.com/acidicoala/SmokeAPI/releases/latest), also pinned in
here) holds six files: `smoke_api32.dll`, `smoke_api64.dll`, their two Linux `.so`
equivalents, a README and `SmokeAPI.config.json`.

Match the **game's** bitness, not your OS's. Task Manager → *Details* → right-click the headers →
*Select columns* → *Platform* shows it while the game runs.

> **Read it off the running process, never off the folder.** A game can ship *both* `steam_api.dll`
> and `steam_api64.dll`, and the one present tells you nothing about the executable that runs. If you
> pick wrong you don't get a subtle failure: a 32-bit DLL simply cannot load into a 64-bit process,
> and vice-versa, so `SmokeAPI.log.log` never appears. Which makes the log a free bitness check — if
> it shows up, you matched.
>
> **And check again after an update.** *A Dance of Fire and Ice* has both a 32-bit and a 64-bit
> Windows depot. The install tested here in August 2026 loaded `smoke_api32.dll`; by October 2026
> (build 24397494) the same install was running a **64-bit** executable, and the 32-bit `version.dll`
> left from that test could no longer load at all. Nothing tells you — the log just stops appearing.

Upstream's advice, worth following: **try hook mode first**, fall back to proxy mode.

### Hook mode (try this first)

Take `smoke_api64.dll`, rename it to **`version.dll`** — or `winhttp.dll`, or `winmm.dll` — and drop
it next to the game executable. Windows loads DLLs from the executable's folder before the system
ones, so the game loads SmokeAPI without anything being replaced.

Its advantage matters more than it looks: **nothing in the game folder is modified**, so a game
update doesn't undo it, unlike everything else in this repo.

If the game loads none of those three DLLs, the injector [Koaloader](#koaloader-when-hook-mode-cant-latch-on)
covers more names — read the section below before using it. Rather than guessing which one, run
[Process Monitor](https://learn.microsoft.com/sysinternals/downloads/procmon) while the game starts,
filtered on the game's process name and on *Path* containing the game folder: it lists every DLL the
game tries to load from its own directory, which is exactly the set you can hijack.

### Proxy mode (fallback)

1. Rename the game's `steam_api64.dll` to **`steam_api64_o.dll`** — the same `_o` convention used
   everywhere in this repo, except that here it's mandatory: SmokeAPI looks for that exact name. It's
   a lowercase letter `o` for *original*, not a zero. Upstream lists the confusion as a recurring
   mistake.
2. Rename `smoke_api64.dll` to `steam_api64.dll` and put it where the original was.

Guaranteed to load, but a game update restores the real `steam_api64.dll` over it — same trap as
everywhere else, see [Updating a game](../game-files/Updating%20a%20Cracked%20Game.md).

---

## Testing it properly

Switching everything on at once tells you nothing: if all the DLC appears, you can't say whether the
unlocker did it or whether you were looking at the wrong screen before. Force **one** DLC you don't
own, and let the rest answer normally.

```json
{
  "$version": 4,
  "logging": true,
  "default_app_status": "original",
  "override_dlc_status": { "717490": "unlocked" }
}
```

`original` passes Steam's real answer through for everything else — DLC you actually own keep
working without the unlocker's involvement. Then only one thing in the entire game can have changed,
and it's the one you named.

Pick a DLC that's **unmistakable in the interface**: a car, a map, a character. Cosmetic or
interface-wide packs make for a frustrating first test — you'll spend the evening looking rather than
observing.

Two places not to look:

- **Steam's own DLC tab** never changes. SmokeAPI answers the *game's* questions, not the client's.
- **Anything with randomised stock** (a shop that rotates its inventory) — absence there proves
  nothing. Find a deterministic list.

`SmokeAPI.log.log` appearing next to the DLL is the primary evidence, before any in-game check: it
means the DLL was loaded and is answering. No log means the injection failed, which is a different
problem from the unlock failing.

### Confirmed working

**Car Mechanic Simulator 2018** (AppID 645630), SmokeAPI v4.1.3, hook mode as `version.dll`,
tested 2026-08-09. Single-player, no anti-cheat, 21 DLC and **zero DLC-gated depots** — the profile
the checks above are looking for. Forcing the Jeep DLC (717490) alone made that car appear and
nothing else moved.

Worth noting that the depot check predicted the outcome before anything was installed. That's the
part to reuse.

### A Dance of Fire and Ice (withdrawn)

Listed under *Confirmed working* in August 2026, **withdrawn in October 2026**, and kept here because the
mistake is the useful part.

AppID 977950, SmokeAPI v4.1.3, hook mode as `version.dll`, tested 2026-08-11. Single-player, no
anti-cheat, and zero of 5 base depots gated — which looked like the Car Mechanic profile. Its one
content DLC is *Neo Cosmos* (1977570); the other two entries in its DLC list are soundtracks. Forcing
1977570 with `default_app_status: original` made SmokeAPI report it owned, and the Neo Cosmos entry
appeared.

What that test didn't check is whether the levels behind it would load. Read in the game's own code
(build 24397494): a DLC counts as *installed* only if two files exist in the game's `Bundles\`
folder — `neocosmos_scenes_all.bundle` and `neocosmos_assets_all.bundle` (about 143 MB). They come
from Neo Cosmos's **own depots** (1977571–1977574, declared under the DLC's app ID, so the base-game
check never sees them), and Steam downloads them only for owners. Without them, the Neo Cosmos screen
says the DLC isn't installed and the levels stay locked, whatever the unlocker answers. Its log says
it plainly too — `%USERPROFILE%\AppData\LocalLow\7th Beat Games\A Dance of Fire and Ice\Player.log`
prints `Neo Cosmos: owns …, installed …` at startup.

Re-tested 2026-10-17 under gbe_fork (SteamAutoCrack 3.5.1.0, `unlock_all=0` with 1977570 listed):
on a copy **without** the two bundles, `owns True, installed False`; on a copy **with** them,
`owns True, installed True` — the state in which the game's code unlocks the Neo Cosmos levels. So it's a game where the unlock works
and the content has to come from your own Steam download — the ETS2 case, not the Car Mechanic one.

---

## Configuration

### Where the file goes, and whether you want one at all

`SmokeAPI.config.json`, **next to the SmokeAPI DLL** — which in hook mode means next to the file you
renamed to `version.dll`, not next to `steam_api64.dll`. It's read at every launch, so changing
behaviour never means reinstalling anything.

**You probably don't need it.** With no config file, SmokeAPI unlocks everything it can, which is
what most people are after.

> **The config shipped in the zip has `logging` set to `true`.** Upstream's own README.txt says it
> outright: don't drop that file in unless you have a reason, because logging costs performance in
> game. If you copy the shipped file, set `logging` to `false` once you're done debugging — or
> delete the file entirely.

Windows will happily save your file as `SmokeAPI.config.json.txt` without telling you. Turn on
*View → Show → File name extensions* in Explorer and check the type column reads *JSON*.

### The three statuses

Every option below resolves to one of three values:

| Value | Meaning |
|---|---|
| `unlocked` | tell the game you own it |
| `locked` | tell the game you don't, even if you do |
| `original` | pass Steam's real answer through, untouched |

`original` is what makes a controlled test possible, and it's also how you leave a specific DLC
alone.

### Precedence

Three levels, most specific wins:

```
override_dlc_status   →  a single DLC, beats everything below
override_app_status   →  every DLC belonging to one AppID
default_app_status    →  the fallback for anything not named above
```

### Recipes

**Everything.** No config file at all. Or, explicitly:

```json
{ "$version": 4, "logging": false, "default_app_status": "unlocked" }
```

**A controlled test** — one DLC forced, everything else answering through Steam:

```json
{
  "$version": 4,
  "logging": true,
  "default_app_status": "original",
  "override_dlc_status": { "717490": "unlocked" }
}
```

**Everything except one** — a pack that breaks the game, or one you intend to actually buy:

```json
{
  "$version": 4,
  "logging": false,
  "default_app_status": "unlocked",
  "override_dlc_status": { "1125210": "locked" }
}
```

**Per-game**, when a title queries entitlements belonging to another AppID:

```json
{
  "$version": 4,
  "default_app_status": "original",
  "override_app_status": { "645630": "unlocked" }
}
```

### Games with more than 64 DLC

Worth knowing before you conclude a game is only half-unlocking. Some titles start by asking
Steamworks for the full DLC list, and **that response can cap out at 64** depending on how many you
don't own. SmokeAPI works around it by asking Steam's web API for the complete list instead — but
that only returns DLC that have a **store page**. Pre-order DLC and other store-less entries fall
through the gap.

Two answers, in order:

1. SmokeAPI automatically fetches a community-maintained list of exactly those store-less DLC IDs
   ([public-entitlements](https://github.com/acidicoala/public-entitlements/blob/main/steam/v2/dlc.json)),
   so most cases resolve with no config at all.
2. If yours isn't in it, name the missing IDs yourself under `extra_dlcs`.

Below 64 DLC — which covers everything discussed in this guide — none of this applies.

### Full option list

| Option | Type | Default | Does what |
|---|---|---|---|
| `logging` | bool | `false` | Writes `SmokeAPI.log.log`. **First thing to turn on when something doesn't work**, and to turn back off afterwards |
| `log_steam_http` | bool | `false` | Also logs the Steam web API traffic. Only useful for the 64-DLC case above |
| `default_app_status` | string | `unlocked` | The fallback status |
| `override_app_status` | object | `{}` | `{"AppID": "status"}` |
| `override_dlc_status` | object | `{}` | `{"DlcID": "status"}`, wins over the app status |
| `auto_inject_inventory` | bool | `true` | Injects the known inventory items when a game queries your inventory |
| `extra_inventory_items` | array | `[]` | Extra item IDs on top of the automatic list |
| `extra_dlcs` | object | `{}` | DLC IDs with no store page — see above |
| `$schema` | string | — | Points at the JSON schema. Keep it: an editor that reads schemas will flag a bad value before the game does |
| `$version` | int | `4` | Config format version. Leave it alone |

### Before you launch

It's JSON, strictly: no comments, no trailing comma after the last entry, IDs quoted as strings on
both sides — `"717490": "unlocked"`, not `717490: unlocked`. A malformed file doesn't announce
itself; you just get default behaviour and a confusing evening.

Turn `logging` on for the first launch after any edit. `SmokeAPI.log.log` appearing tells you the
DLL loaded and read your file — which separates "my config is wrong" from "the injection failed",
two problems that look identical from inside the game. Turn it off again afterwards: in some games
the log grows past 100 MB.

From the release thread (cs.rin.ru, 2022–2026), the pitfalls people actually hit:

- **The log describes the wrong process.** In hook mode the DLL can be picked up by a helper the game
  starts — `UnityCrashHandler64.exe`, `crashpad_handler.exe` — and the log you're reading is that
  helper's. Rename the helper and try again.
- **Hook-mode and proxy-mode files left side by side** break both. Clean one install out completely
  before trying the other.
- **A launcher is not the game.** Paradox titles and Bannerlord load the Steam API in the launcher
  differently from the game itself; check which executable the log comes from.
- **Under Proton** (Steam Deck), hook mode needs the override as a launch option:
  `WINEDLLOVERRIDES="version=n,b" %command%` (use the DLL name you installed as).
- **`"default_app_status": "original"`** answers the truth for everything you don't override — handy
  when you only want one DLC unlocked and the rest left as Steam reports it.
- **`"auto_inject_inventory": false`** fixes in-game item pop-up spam (Golf With Your Friends) and
  crashes (Bloons TD 6).

---

## When it won't work

Assuming it passed the [candidate checks](#is-this-game-even-a-candidate), there are still cases
where it won't. Upstream is unusually honest about them, and they're worth reading before blaming
the install:

- **Third-party DRM** (Ubisoft, Rockstar and friends) — the check isn't Steamworks' to answer.
- **Denuvo SecureDLC** — see [Denuvo](Denuvo.md).
- **Free-to-play games** — entitlements live on the game server, nothing client-side to fool.
- **Anti-cheat** — it inspects tampered DLLs, and this is how accounts die. Don't.
- **Server-checked ownership** — Hitman 3, World of Trucks, The Bazaar: the answer that counts comes
  from a server, not from the DLL.
- **Games with their own ownership checks** on top of Steamworks. Common enough.
- **DLC whose files aren't installed.** Unlocking says "you own it"; it doesn't download anything. If
  the game only fetches DLC assets after purchase, you'll unlock an entry that has no content behind
  it.

A game with no `steam_api.dll` / `steam_api64.dll` at all is simply not a candidate.

---

## Doing all of it automatically

[CreamInstaller](https://github.com/FroggMaster/CreamInstaller) (GPL-3.0, actively maintained) scans
your machine for installed Steam, Epic and Ubisoft games, finds the DLL locations, pulls each game's
DLC list from SteamCMD and the store, and installs a configured unlocker for the ones you tick. It's
the automated version of this entire page, and for a large library it saves a real amount of
clicking.

One thing to know before running it: **it embeds every unlocker it installs**, CreamAPI and ScreamAPI
included. Those are precisely the two this repo won't recommend — one has never had a public
repository, the other's is
[blocked](#what-about-eos-dlc) — so for those, the binaries inside CreamInstaller cannot be compared
against anything upstream. Its own source is readable and its SmokeAPI path is the same tool
described above.

Reasonable use: let it do the discovery, and prefer the games where what it installs is SmokeAPI.

What its maintainer and users report from running it (cs.rin.ru release thread, Jan–Oct 2026):

- **Tick the DLC you already bought too.** Whatever is left unticked is answered "not owned" — a
  Generation Zero owner who ticked only the one DLC he lacked lost the six he'd paid for until he
  re-ran it with all of them selected. Simplest rule: leave every DLC of the game ticked.
- Since v5.1 it never uses Koaloader for Steam games: SmokeAPI goes in either as a straight
  replacement or as a proxy (`winmm.dll` by default; `version.dll` when a game ignores that one).
- SmokeAPI answers *every* DLC by default; CreamAPI only answers the ones listed. If a game rejects
  SmokeAPI, unticking it makes CreamInstaller fall back to CreamAPI — and for games that check the
  Steam DLL itself, CreamAPI's `extraprotection = true` (a checkbox in the current pre-release)
  keeps the original DLL in place. Crimson Desert needed exactly that.
- A DLC released after the last scan can be missing: right-click the game → **Refresh Queries**.
- Unlocked DLC don't appear in Steam's DLC tab — expected, and harmless.
- **Paradox games** (Stellaris, Hearts of Iron IV, Crusader Kings III, Europa Universalis, Victoria
  3) go through the Paradox Launcher, which lives outside the game folder — its real location is the
  `LauncherInstallation` value under `HKCU\Software\Paradox Interactive\Paradox Launcher v2`
  (default `%LOCALAPPDATA%\Programs\Paradox Interactive`). Every launcher update creates a new
  `launcher-v2.*` folder, so the unlock has to be re-applied (CreamInstaller's right-click *Repair*
  exists for that). And "unable to verify ownership" in the launcher is often cosmetic: users report
  the DLC working in-game, achievements included, while the launcher still says it.
- Reported as not working at all: Payday 2, Euro Truck Simulator 2 1.59, Automobilista 2, Le Mans
  Ultimate, Hitman World of Assassination, Total War: Warhammer III, Dead or Alive 6, Victoria 3 /
  Hearts of Iron IV, Borderlands 4 — plus anything with Denuvo, Easy Anti-Cheat, or content that
  lives on the publisher's servers.

**Which CreamInstaller.** There are two lines, and you'll be handed the wrong one sooner or later:

- **FroggMaster's** — the link above. Not a GitHub fork, its own repository, GPL-3.0, releasing
  (v5.2.0.0 on 2026-10-07). This is the one to use.
- **pointfeev's** — the original. Its repository has been **DMCA-blocked since 2024-10-14** (GitHub
  answers HTTP 451), so its last release, **v5.0.0**, now only circulates as reuploads on file hosts,
  with nothing upstream left to diff against. One such copy was checked on 2026-10-02: version info
  `5.0.0.0` / pointfeev, exe sha256 `690ef7fc…9d73`, **first seen by VirusTotal on 2024-07-23** — the
  day after its build date — with some 28,000 submissions since. That history is what makes it
  credible: it's the widely circulated genuine build, not a recent repack. Its 5/69 detections are all
  Koaloader riskware, the loader it embeds, and no stealer family. Not executed.

  If you're handed a v5.0.0 whose hash differs from that one, treat it as unknown. Either way it's
  frozen at mid-2024 — there's no reason to prefer it over FroggMaster's.

And one to avoid by name: **`ubden/CreamApi-CreamInstaller`**, a GitHub fork (of a fork) with some
1,400 stars and a polished README. In September 2026 a user reported on its own discussion page (#47)
and on cs.rin.ru that installing it led to a compromised machine, with Windows Security flagging the
download. Checked here on 2026-10-10, by hash only: its `CreamInstaller.exe` (release `v5`, sha256
`c301d783…bcad3c23`) scores **31/75** on VirusTotal, labelled `trojan.generickdq`, where FroggMaster's
current exe scores 4/75 — generic labels (`UDS:DangerousObject`, `Backdoor.Agent` from one engine),
and in VirusTotal's sandbox its only network traffic is `api.github.com/repos/FroggMaster/CreamInstaller/releases`,
its own update check. On the ubden build, a sandbox run shows nothing conclusive, so this is not proof of malware —
but nothing about it beats FroggMaster's, and the contrast is enough. Not executed.

**What Valve has actually done about it.** In June 2024 the forum staff announced that "Steam is now
blocking this tool", and the author confirmed it in August 2025: Valve "started targeting SmokeAPI in
their Steam process" — a *warning shot*, his words, aimed at the **store mode** that ran inside the
Steam client itself (used by Koalageddon). He chose not to escalate and removed store mode in v3.0.
Nothing in four years of the thread reports a ban, and every warning report involves code running
inside Steam, not the in-game DLL this page uses. That's the evidence; it's not a guarantee — the
in-game DLL is still a modified file next to a logged-in Steam.

Upstream of all of them, note that **acidicoala** — author of SmokeAPI, Koaloader and ScreamAPI —
announced on **2026-02-16** that he is on hiatus "for the foreseeable future". SmokeAPI v4.1.3
(2026-01-18) is the last release; nothing is broken today, but don't expect fixes when Steam changes.

---

## Linux-native games

Everything above is about Windows DLLs. A native Linux build loads `libsteam_api.so` instead, and
SmokeAPI's own `.so` files cover the common case. A self-contained alternative that you build
yourself is [CreamySteamyLinux](https://github.com/lemon07r/CreamySteamyLinux) (MIT, v2.0.0,
2026-06-29): a small C proxy for `libsteam_api.so`, compiled on your machine for each game, with the
original kept as `steam_api_o.so`. `./deploy.py <game folder>` reads the AppID from the
`appmanifest_*.acf`, fetches the DLC list from the store and writes `cream_api.ini`;
`--status`, `--restore` and `--uninstall` do what they say. One trap: **every deploy rewrites the ini
with all DLC** — edit it once, then redeploy with `--no-fetch`. Tested by its author on Victoria 3,
BATTLETECH and Across the Obelisk; a Hearts of Iron IV launcher crash was unresolved.

Built from source on your own machine, it's the most auditable option on this page — and it has
seven stars, so you are the audit.

---

## Koaloader, when hook mode can't latch on

[Koaloader](https://github.com/acidicoala/Koaloader) is a bag of 89 DLLs named after things games
load (`d3d11.dll`, `dxgi.dll`, `xinput9_1_0.dll`, `audioses.dll`…), each of which loads
`smoke_api64.dll` for you. You use it when the game ignores `version` / `winhttp` / `winmm`.

**Check what you're running before you use it.** Same author, same licence, but the numbers are not
the same as the rest of this repo (checked 2026-08-09):

| File | VirusTotal | Labels |
|---|---|---|
| `smoke_api64.dll` | 5/71, 1555 submissions | `Artemis!`, `BehavesLike…`, generic heuristics — the usual shape for these tools |
| Koaloader `version.dll` | 31/72, 48 submissions | `Gen:Variant.Mikey`, `Win64:MalwareX-gen`, `Trojan/Win32.Agent` |
| Koaloader `d3d11.dll` | 30/72, 52 submissions | same |

Those Koaloader labels are still generic — no named stealer, no miner, no RAT — and a DLL that
impersonates `d3d11.dll` to inject another DLL is textbook enough that engines flag it on shape
alone. But it's a low-prevalence binary carrying malware-family generics rather than the
`GameHack`/`PUA` bucket the emulators sit in, and I can't tie the published binary to the published
source without building it.

So: it's **not recommended here as a default**, on purpose. If you need it, get it from upstream,
decide for yourself, and prefer plain hook mode whenever it works.

---

## What about EOS DLC?

The equivalent tool for Epic Online Services was **ScreamAPI**, by the same author. As of
**2026-07-28 its GitHub repository is blocked for a terms-of-service violation** — no README, no
releases, nothing to download from the official source. Its successor **Koalageddon 2**, which
covered Steam, EOS and Ubisoft together, was **archived in October 2025**.

Which means every ScreamAPI copy you'll find is a third-party reupload with no way to check it
against anything — exactly the [RUNE](../running/RUNE%20Steam%20Emulator%20User%20Guide.md) situation,
minus the reputation. Nothing here recommends one.

Note this is unrelated to [eos-proxy](../multiplayer/EOS%20Proxy%20Usage%20Guide.md), which fixes an
EOS *login* and has nothing to do with entitlements.

---

## Links

- SmokeAPI: https://github.com/acidicoala/SmokeAPI
- Koaloader: https://github.com/acidicoala/Koaloader
- DLC IDs: https://steamdb.info/ — the *DLC* tab of the game's page
  (copy them by hand: SteamDB forbids scraping and has planted at least one fake entry,
  `737430707363726170` — hex for `st0pscrap` — that scripts copied into `cream_api.ini` and that
  crashed games. A DLC ID is a 32-bit number; anything longer is not a DLC)
