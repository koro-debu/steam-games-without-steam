# Steam Games Without Steam

Notes on running, unpacking and inspecting games **you own** when the Steam client is in the way:
playing offline, playing on a LAN, modding, and reverse engineering.

Written for future me, who will have forgotten all of it. If that's you right now, read the next two
sections and ignore everything else until you need it.

> **Scope:** written for games you own. None of these tools unlocks a purchase — they emulate the
> Steam API around files you already have, and Steam refuses to hand out depot keys to an account
> that doesn't own the app. Circumventing DRM can be illegal in your country even for personal use
> (DMCA in the US, EUCD in the EU).

---

## How any of this works, in one minute

A Steam game asks Steam two kinds of question: *"who am I talking to"* and *"is this person allowed
to play"*. It asks through a file sitting in its own folder, **`steam_api64.dll`**.

Every tool here does the same trick: **swap that file, or one like it, for a version that answers by
itself.** The game can't tell the difference. That's the whole idea — nothing patches the game.

Which tool you need depends on *which* question is blocking you:

| The blocker | The tool |
|---|---|
| The game wants Steam running | replace `steam_api64.dll` with an emulator |
| The `.exe` itself refuses to start | unwrap it first, then do the above |
| Multiplayer is dead | depends on what its multiplayer runs on |
| A DLC shows as locked | a different DLL, answering ownership questions |

They stack: one tool for the executable, one for the API, one for multiplayer. Nothing here
conflicts, except where a guide says so explicitly.

### Words you'll meet

| Term | What it means, practically |
|---|---|
| **AppID** | The game's number on Steam. In the store URL, or on [SteamDB](https://steamdb.info/). Every guide needs it |
| **`steam_api64.dll`** | The file the game talks to Steam through. The 32-bit one is `steam_api.dll` |
| **Emulator** | A replacement for that file. gbe_fork, RUNE |
| **SteamStub** | A wrapper around the `.exe` itself. Steamless removes it |
| **Depot** | A chunk of the game's files on Steam's servers. Downloading one needs a licence |
| **DLC** | Sold separately. Sometimes its files ship with the base game, sometimes not — that difference decides everything |
| **EOS** | Epic Online Services. Some Steam games run their multiplayer on Epic's servers |
| **Denuvo** | Anti-tamper DRM welded into the game's own code. Nothing here removes it — but gbe_fork can run a game you own with a ticket from your own account |

---

## What do you want to do?

| I want to… | Go to |
|---|---|
| **Know whether this game is even worth trying** | [Denuvo list](lists/Denuvo.md) · [anti-cheat list](lists/Anti-Cheat.md) — **check these first** |
| Play a game I own without the Steam client running | [Goldberg / gbe_fork](running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) |
| …but the game won't even start | [Steamless](running/Steamless%20Usage%20Guide.md), then back to Goldberg |
| Have all of it done for me in one pass | [RUNEAutoCracker](running/RUNEAutoCracker.md) — read what it installs first |
| Play with a friend | [Which tool, and with whom](multiplayer/Multiplayer%20Routing.md) |
| Get multiplayer working when the game uses Epic | [EOS Proxy](multiplayer/EOS%20Proxy%20Usage%20Guide.md) |
| Unlock a DLC on a game I own, with Steam running | [DLC Unlocking](other/DLC%20Unlocking.md) |
| Download game files without the client, or an older build | [DepotDownloader](game-files/DepotDownloader.md) |
| Understand what broke after a game update | [Updating a game](game-files/Updating%20a%20Cracked%20Game.md) |
| Keep my saves, and get achievements working | [Saves & achievements](game-files/Saves%20and%20Achievements.md) |
| Check that downloaded game files are unmodified | [`verify_base.py`](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#check-that-base-before-you-build-on-it) |
| Unlock achievements on my real account | [SAM](other/Steam%20Achievement%20Manager%20(SAM)%20Usage%20Guide.md) |
| Do the whole thing from scratch, end to end | [The generic guide](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md) |
| Find out why nothing works on this particular game | [Denuvo](other/Denuvo.md), most likely |
| Play a Denuvo game I own without the Steam client | [Denuvo — a ticket from your own account](other/Denuvo.md#running-a-denuvo-game-you-own-without-the-steam-client) |
| Know why SteamTools / CreamAPI / Online-Fix aren't here | [What's not in this repo](other/Closed-Source%20Tools.md) |

---

## Five rules that apply to everything here

1. **Back up before you replace.** Each guide says which file. Keep the original with `_o` before its
   extension — `steam_api64_o.dll`, `Game_o.exe`. You will need it.
2. **"Game folder" means where the `.exe` is.** On Unreal titles that's `<Game>\Binaries\Win64\`, not
   the folder you land in first. Files in the wrong place fail silently, with no error to search for.
3. **Anti-cheat means stop.** VAC, EasyAntiCheat, BattlEye — EAC and BattlEye ship in plenty of
   Steam games too, not just Epic ones. Nothing here tries to defeat any of them, and a ban is
   permanent. VAC in particular leaves **no files in the game folder**, so looking won't tell you:
   [the list](lists/Anti-Cheat.md) will.
   **Playing offline is a separate question.** Most of these games run their campaign without the
   anti-cheat ever loading, and Steam's own offline mode covers it — no tools, no risk.
4. **Your antivirus will flag all of it.** Expected for this category — [further down](#verifying-what-you-download)
   is how to tell a real problem from the usual noise.
5. **Not on family-shared games.** The licence belongs to someone else, and the consequences land on
   their account.

---

## Which layer do I need? — the decision flow

Once the vocabulary above makes sense, this is the whole repo on one screen:

```text
Does the store page say "Requires 3rd-Party DRM: Denuvo Anti-tamper"?
│
├─ Yes → you own it? gbe_fork + a ticket from your own account (Denuvo page, first section).
│        Not yours, or that fails → nothing else here applies
│
└─ No ↓

Install gbe_fork first — it is the layer nearly every game needs.
│
├─ The game doesn't start
│  └─ "Steam must be running" / instant close
│     └─ The .exe is wrapped in SteamStub → Steamless, then back here
│
└─ The game starts
   │
   └─ Does the store page list Multi-player / Online Co-op / Online PvP?
      │
      ├─ No → nothing to fix. Stop here: plenty of single-player games ship
      │       EOSSDK-Win64-Shipping.dll for save sync or achievements
      │
      └─ Yes ↓
         │
         └─ Is there an EOSSDK-Win64-Shipping.dll in the game folder?
            │
            ├─ Yes — the login very likely goes through Epic
            │  └─ add eos-proxy. Where the sessions really run on EOS you end
            │     up alongside people who bought the game normally
            │
            └─ No — the multiplayer is Steam's, or something else entirely
               └─ gbe_fork alone → LAN only, so virtual LAN or custom_broadcasts.txt
                  Anything more (real matchmaking, Photon, PlayFab) → see Multiplayer routing
```

A game can also keep its own backend behind all of that, and then no client-side tool reaches it —
which is why [Multiplayer routing](multiplayer/Multiplayer%20Routing.md) is the page to read before
installing anything.

The three layers it walks through:

| Layer | Problem it solves | Tool |
|---|---|---|
| **Executable** | The `.exe` is wrapped in SteamStub and refuses to run without Steam | Steamless |
| **Steam API** | The game calls `steam_api64.dll` and expects a live Steam session | gbe_fork / RUNE |
| **EOS** | Multiplayer runs on Epic's servers and the login asks Steam for a ticket | eos-proxy |

Most games need the middle one and nothing else.

---

## All the guides

#### Making a game run

| Guide | What it covers |
|---|---|
| [Goldberg / gbe_fork](running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) | The Steam API layer, and the one to try first. Player name, DLC, saves, overlay |
| [RUNE](running/RUNE%20Steam%20Emulator%20User%20Guide.md) | Simpler alternative to gbe_fork. Unmaintained, unauditable — fallback only |
| [RUNEAutoCracker](running/RUNEAutoCracker.md) | Does the RUNE route in one pass, DLC list included. The only automated tool here, and the checks it needed |
| [Steamless](running/Steamless%20Usage%20Guide.md) | Remove the SteamStub wrapper when the executable itself refuses to start |

#### Multiplayer

| Guide | What it covers |
|---|---|
| [Which tool, and with whom](multiplayer/Multiplayer%20Routing.md) | Routing by backend — and who you end up able to play with. **Read this one first** |
| [EOS Proxy](multiplayer/EOS%20Proxy%20Usage%20Guide.md) | Games whose netcode runs on Epic rather than Steam |
| [uc-online2](multiplayer/uc-online2.md) | Steam's real matchmaking, by reporting a different AppID. Also Photon, PlayFab, coherence |

#### Game files

| Guide | What it covers |
|---|---|
| [DepotDownloader](game-files/DepotDownloader.md) | Pull files from Steam without the client — a clean base, or one specific build |
| [Updating a game](game-files/Updating%20a%20Cracked%20Game.md) | What a new build silently breaks, and what has to be redone |
| [`verify_base.py`](game-files/verify_base.py) | Check a base that didn't come from Steam: is its manifest genuine, and are the files exactly what it lists — [how to use it](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#check-that-base-before-you-build-on-it) |
| [Saves & achievements](game-files/Saves%20and%20Achievements.md) | Where your saves go under the emulator, how to bring them across, and getting achievements back |

#### Before you start

| List | What it covers |
|---|---|
| [Denuvo — the full list](lists/Denuvo.md) | 190 games Steam still declares, 56 where the two sources disagree, and **157 where Denuvo was removed** and everything here works again (re-checked 2026-10-10) |
| [Anti-cheat — the full list](lists/Anti-Cheat.md) | 590 games, by product. VAC leaves no files on disk, so looking in the folder will not tell you |

#### Everything else

| Guide | What it covers |
|---|---|
| [SAM](other/Steam%20Achievement%20Manager%20(SAM)%20Usage%20Guide.md) | Achievements on your own account. Works *with* Steam, not around it |
| [DLC Unlocking](other/DLC%20Unlocking.md) | SmokeAPI: locked DLC on a game you own, **with Steam running normally** |
| [Denuvo](other/Denuvo.md) | Running a game you own with gbe_fork and your own account's ticket (5 activations a day, 30-minute ticket), why the rest doesn't apply, how to recognise it early — and what a hypervisor bypass costs your PC |
| [What's not in this repo](other/Closed-Source%20Tools.md) | The two rules that decide what gets a guide — scope and auditability, where the shared manifests come from, and **one Online-Fix package taken apart** |
| [The generic guide](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md) | The whole path end to end, worked out on a real game |

---

## Known limits

- **Online multiplayer through Steam does not work.** What you get is LAN discovery. To play with
  someone elsewhere: a virtual LAN (Radmin VPN, Hamachi, ZeroTier), or their public addresses in
  gbe_fork's `steam_settings\custom_broadcasts.txt` — port forwarding is on you. The fuller answer is
  [Multiplayer routing](multiplayer/Multiplayer%20Routing.md).
- **Multiplayer through Epic (EOS)** is the exception: its own layer, and it puts you in sessions
  with people who bought the game — see the [EOS Proxy guide](multiplayer/EOS%20Proxy%20Usage%20Guide.md).
- **Denuvo** is a different problem: nothing here removes it. A game you own can still run through
  gbe_fork with a ticket from your own account, capped at 5 activations a day —
  [how, and what's left to you otherwise](other/Denuvo.md). **EA App and Ubisoft Connect** are out of scope entirely.
- **32-bit games** use `steam_api.dll` and the `x86` folders, not `steam_api64.dll` / `x64`. The
  guides use the 64-bit names throughout; substitute as needed.
- **Some games detect the emulator and say so, minutes after launch.** Not at startup — late enough
  that you'll have concluded it worked. Two gbe_fork defaults cause most of it and both are
  configurable, but not all of it:
  [when the game says it's a pirated copy](running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md#the-game-says-its-a-pirated-copy).
- **A server that validates a Steam ticket cannot be fooled**, by any client-side tool, ever.
  Peer-to-peer fixes work; server-side validation doesn't. That one line explains most of the
  failures people report.

---

## Verifying what you download

The **Releases** tab of this repo pins the exact copies these guides were written against, so you can
always tell which build a guide describes. Upstream comparison done 2026-08-09 (gbe_fork and
SteamAutoCrack 2026-10-10); every pinned digest below re-checked against the live Releases tab on
2026-10-10:

| Release | sha256 | Matches upstream? |
|---|---|---|
| `emu-win-release.7z` (gbe_fork `release-2026_09_27`, upstream `emu-win-release-vs22.7z`) | `300186c3…4e11c85` | yes, byte for byte |
| `emu-win-release-2026_08_23.7z` (gbe_fork `release-2026_08_23`) — previous pin, kept | `812dd5f6…5579baf` | yes, byte for byte |
| `emu-win-release-2026_07_19.7z` (gbe_fork `release-2026_07_19`) — previous pin, kept | `3ba855ef…d972e5` | yes, byte for byte |
| `Steamless.v3.1.0.5.-.by.atom0s.zip` | `e3e2d22e…6d2dc4f5` | yes, byte for byte |
| `SteamAchievementManager-7.0.41.zip` | `6682a333…2d5cd072` | yes, byte for byte |
| `EOSSDK-Win64-Shipping.dll` (eos-proxy v1.0.0) | `00e0f034…0d23916` | yes |
| `eos-proxy-dev-8c5c959-source.zip` — source for the `dev` commit the guide has you compile | `1a2ccaa2…6276aa8d` | source snapshot, nothing to compare |
| `SmokeAPI-v4.1.3.zip` | `8a443b5b…8c1d2a3b` | yes, byte for byte |
| `RUNE.Steam.Emulator.zip` | `bde10c56…86c5b71f` | **no upstream to compare against** — see the [RUNE guide](running/RUNE%20Steam%20Emulator%20User%20Guide.md) |
| `TENOKE.Steam.Emulator.zip` | `259ac4ed…3b5b590e` | **no upstream to compare against** |
| `SteamAutoCrack.zip` (v3.5.1.0) | `86853fe9…997de3d9` | yes, byte for byte — and it bundles gbe_fork `release-2026_09_16_2` (vs26) and [Steamless-KR](https://github.com/K0oRui/Steamless-KR), not atom0s' Steamless |
| `SteamAutoCrack-3.5.0.7.zip` — previous pin, kept | `8a93d60d…09c81043` | yes, byte for byte |

**Reading a VirusTotal result on these tools.** A high score is normal and mostly meaningless here.
`emu-win-release.7z` sits around 28/61 and gbe_fork's `steamclient_loader_x64.exe` around 36/70,
under labels like `Trojan.Win32.GameHack`, `RiskWare/Win64.Gamehack`, `7zip.trojan.generic`,
`Unwanted-Program` and `Malware.AI` — that is the *category* "Steam emulator" plus generic
heuristics, not a malware family. The DLL you actually drop into a game folder
(`release\regular\x64\steam_api64.dll`) comes back **0/71**, and that is the number that matters:
the loader scores because it injects into the game process, which every engine flags on principle.
The current pin also draws one `Backdoor.Win32.RevShell` from a single engine, on the archive only —
no file inside carries it, which is why it's read as a heuristic; the
check was done file by file.

What's worth reacting to is a **named** family (a stealer, a miner, a RAT), a **behaviour** report
showing network traffic or registry persistence, or a hash that **doesn't match** the upstream
release. Score alone tells you nothing.

**The download page is the riskier half.** Most infections around these tools don't come from the
tool, they come from the page you fetched it from. The pattern, as documented by the cs.rin.ru staff
in September 2026: on a number of popular file hosts, the first click on the download button opens a
*second* tab that imitates a known host, on an odd domain (`.website`, `.shop`, `.cfd`, `.sbs`, with
random numbers in it), and serves a zip. Inside is an info stealer **disguised as a Ren'Py game**, under
a file name copied from the real upload — and Windows Defender doesn't stop it. What works:

- **uBlock Origin on Firefox** (or Mullvad Browser, which ships with it). On Chrome only uBlock
  Origin *Lite* is left, and its filter updates are too slow to keep up with these domains.
- **Or a download manager** (JDownloader 2): paste the link, and the host's page never loads in a
  browser at all.
- Close any tab you didn't open yourself, and treat a "game" zip where you expected a DLL as the
  alarm it is.
- Know the names. As of October 2026 the forum staff list these as still serving malware ads:
  **akirabox** (`.com`/`.to`, to be banned there on 2026-12-01), **datavaults.co** (2026-11-01),
  **rootz.so**, the multi-uploaders **multiup.io** and **mirrored.to**, and **buzzheavier** /
  **fuckingfast** and **datanodes** on probation. Already banned there for it: `devuploads`,
  `bowfile`, `1cloudfile`, `ranoz`, `swiftuploads`, `usersdrive`, `koramaup`, `filemirage`, `fileq`,
  `file-me.top`, and a string of sites impersonating repackers (`dodi-repacks.*`, `elamigos*`,
  `steam-repacks.*`, `game-repack.site`, `repack-games.com`, `steamunderground.net`…). A link
  aggregator (pastebin, Filecrypt, Multiup) that points at one of these is no safer than the host.
- **"Crack" and "keygen" sites found through a search engine are the same trap, older.** The
  pattern, taken apart on Tuts4You in 2020–21 (keygens.pro, keygenninja.com, cracknet.net and a
  dozen sister domains sharing one server): whatever you ask for, you get a **password-protected
  archive** with the password printed on the page (`123`, `12345`) holding a `setup_pass-123.exe` or
  a self-extracting archive. The password is there so the scanner of the site, of your browser and
  of your antivirus can't look inside before you run it. What came out was named families — Remcos
  and PoisonIvy (remote access), Vidar and CopperStealer (saved passwords and browser cookies) —
  around 10,000 installs a day for the busiest site. The domains rotate; the shape doesn't. A
  release group's name and an `.nfo` in the archive prove nothing — they were copied too. And
  **paying doesn't change it**: a March 2026 thread there is someone who bought a $7 "crack" that
  worked and was a RAT as well.

The tools in this repo don't have that problem — they come from GitHub release pages. It's the
[mirrors for game files](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#3-get-an-unmodified-base)
and anything off a forum where it bites — and for game files there's a check:
[`verify_base.py`](Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#check-that-base-before-you-build-on-it) compares them with the depot's manifest, and the manifest with Steam.

**When you can't verify it, contain it.** For a file with no upstream to compare against — the
[closed-source tools](other/Closed-Source%20Tools.md) above all — the next best thing is to run it
somewhere it can't reach your real Steam install: **Windows Sandbox** (Pro/Enterprise/Education:
*Turn Windows features on or off* → *Windows Sandbox*). It's a throwaway Windows that starts clean
every time. Three things to know:

- **Everything inside is erased when you close it** — tools you installed, a Steam client you logged
  into, all of it. Do the whole test in one sitting.
- **Don't log into an account you'd miss** inside it. The sandbox protects your machine, not
  whatever credentials you type into it; a stealer run in there still sends what it finds.
- **On Windows 11 26H2 (build 26300) the sandbox can blue-screen** (`0x3B`, in the
  virtual GPU path) as soon as something inside uses the GPU — a browser opening a page is enough.
  Launch it from a `.wsb` file that turns the virtual GPU off instead of from the
  Start menu icon. A text file named e.g. `Sandbox (no GPU).wsb`, saved as plain ASCII **without a
  BOM** — Windows Sandbox won't read the file if it has one:

  ```xml
  <Configuration><vGPU>Disable</vGPU></Configuration>
  ```

  Add `<MappedFolders>` there if you want to pass files in; everything else works as usual.
- **It needs the Windows hypervisor.** Anything that turns that off — a
  [hypervisor-based Denuvo bypass](other/Denuvo.md#hypervisor-bypasses--what-they-cost) in
  particular — takes Windows Sandbox (and WSL 2) down with it until you switch it back on.

---

## A different job: tools that add games to the Steam library

Everything above is about running a game you own **without** the Steam client. A separate family of
tools does the opposite — it gets the **Steam client itself** to list and download a game, from a lua
file and the depot manifests. You'll meet them in every forum thread, so they get a mention here, set
apart, rather than a guide:

- **[LuaTools](https://github.com/madoiscool/LuaTools)** — MIT, C#/WPF. A manager for SteamTools'
  lua files and manifest sources.

- **[Arachnel](https://github.com/BadKiko/Arachnel)** — an open-source launcher whose reference
  plugins point at download sources.

Why they stay out of the guides — they decide what the Steam client believes you own, which is a
different question from running what you bought — is spelled out in
[What's not in this repo](other/Closed-Source%20Tools.md#steamtools-and-everything-that-manages-it).

---

## Upstream projects

| Tool | Repository |
|---|---|
| Goldberg fork (gbe_fork) | https://github.com/Detanup01/gbe_fork |
| Steamless | https://github.com/atom0s/Steamless |
| Steam Achievement Manager | https://github.com/gibbed/SteamAchievementManager |
| eos-proxy | https://github.com/yesyes0649/eos-proxy |
| uc-online2 (active fork) | https://github.com/LukeWarmSodas/uc-online2 |
| SmokeAPI | https://github.com/acidicoala/SmokeAPI |
| DepotDownloader | https://github.com/SteamRE/DepotDownloader |
| SteamAutoCrack (automates the Goldberg step) | https://github.com/SteamAutoCracks/Steam-auto-crack |
| GSE-Generator (achievement and DLC configs) | https://github.com/brunolee-GIT/GSE-Generator |
| gse_fork_tools (maintained `generate_emu_config`) | https://github.com/alex47exe/gse_fork_tools |
| Achievement Watcher Next | https://github.com/Shirowwww/Achievement-Watcher-Next |
| RUNE | *none — no official repository exists* |
| SteamDB (AppIDs, depots, DLC) | https://steamdb.info/ |
| PCGamingWiki (DRM info) | https://www.pcgamingwiki.com/ |
