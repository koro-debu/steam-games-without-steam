# Clean Base + Open-Source Crack + Multiplayer

Worked out on *Big Walk* (AppID 1478500) and written down while it was still fresh. Nothing here
is specific to that game — the same handful of moves apply to any Steam title that ships Steamworks
and, optionally, Epic Online Services for its netcode.

The point of doing it this way is that **every binary involved is one you can read the source of**.
Scene releases and OnlineFix work too, but they hand you an obfuscated DLL and you either trust it
or you don't. Here you don't have to.

> Same framing as the rest of this repo: this is about games you own, or about getting a clean
> base you can inspect. Owning the game also makes step 3 five minutes shorter.

---

## 1. Work out what you're dealing with

Before touching anything, three questions: which AppID, which DRM, and what runs the multiplayer.

| What | Where |
|---|---|
| AppID | The store URL, or [SteamDB](https://steamdb.info) |
| DRM and middleware | [PCGamingWiki](https://www.pcgamingwiki.com), sections *DRM* and *Middleware* |
| Does it use EOS? | Look for `EOSSDK-Win64-Shipping.dll` — often not in the root, try `Plugins\x86_64` and `Binaries\Win64` |
| Does it use Steamworks? | Look for `steam_api64.dll`, same story about subfolders |

The EOS answer decides everything in step 5, so find that DLL before you start — and check the
store page's category list while you're there, because an EOS DLL in a game with no declared
multiplayer means nothing.

---

## 2. Read the existing crack (optional, but do it once)

If a scene release of the game exists, diff its folder against the official one. Anything present
in the release and absent from the Steam copy is something the cracker added:

| File | What it's doing there |
|---|---|
| `winmm.dll`, `version.dll`, `winhttp.dll`… | Proxy DLLs — Windows loads them from the game folder before the system ones |
| `steam_api64.dll` that doesn't match Valve's | The emulator itself, usually packed |
| `OnlineFix64.dll`, `SteamOverlay64.dll` | Online-Fix's networking and overlay |
| `*.ini`, `dlllist.txt` | Their config |

Fifteen minutes of this teaches you more about how these things work than any guide. It also makes
the argument for the open-source route on its own: the packed DLLs can't be audited, by anyone,
ever.

---

## 3. Get an unmodified base

**If you own the game**, download it from Steam, or use [DepotDownloader](game-files/DepotDownloader.md) if you
want a clean copy sitting outside the Steam library — which you do, because Steam updates over
anything left inside it.

**If you don't**, the depot has to come from somewhere else. The game's thread on
[cs.rin.ru](https://cs.rin.ru/) lists depot and manifest IDs:

```
DepotDownloaderMod.exe -app <APPID> -depot <DEPOTID> -manifest <MANIFESTID> -dir "<FOLDER>" -username <USERNAME>
```

Note this is **DepotDownloaderMod**, a fork, not the [DepotDownloader](game-files/DepotDownloader.md) above:
it accepts depot keys and manifest files supplied by hand, which is the only reason it appears in
those threads. The flags are otherwise the same.

Steam only hands out the depot key to accounts that own the game, so an account that doesn't will
get `AccessDenied` here — that's the wall, not a misconfiguration. The threads carry mirrors
(rootz.so, multiup.io) for that case; archive password is `cs.rin.ru`.

Those mirrors are covered in malicious ads. Run [uBlock Origin](https://ublockorigin.com/), ignore
every download button that isn't the real one, and don't install anything they offer you — the
current trap, a fake second tab serving a stealer dressed as a Ren'Py game, is described in
[the README](index.md#verifying-what-you-download). The whole point of this method is not running
unknown binaries — don't lose that at the download stage.

### Check that base before you build on it

A base that didn't come from Steam is only "clean" if someone says so. Uploads of this kind usually ship
the depot's `.manifest` next to the files, and that is enough to check both, with
[`verify_base.py`](game-files/verify_base.py) (Python 3, standard library only, writes nothing):

```
python verify_base.py <DEPOTID>_<MANIFESTID>.manifest "<FOLDER>"
```

1. **Is the manifest genuine?** Steam addresses every chunk of game data by its SHA-1, and its content
   servers answer a request for a chunk's *headers* with 200 if it exists and 404 if it doesn't — with
   no account and without sending the data. The script asks about a sample spread over the depot. A
   manifest made up or edited by hand lists chunks Steam has never seen. (The method is from
   cs.rin.ru's "Validating manifest chunk hashes through Steam")
2. **Are the files the ones it lists?** Each file's size and SHA-1 is compared with the manifest, and
   anything in the folder the manifest doesn't know about is listed separately — on an unmodified base
   that list is empty, so a `steam_api64_o.dll` or a stray `.exe` shows up right there.

`RESULT: matches` means the files are exactly what Steam shipped for that build. What it can't tell
you: whether the *build* is the one you wanted (check the manifest id against SteamDB), and nothing
about files you add afterwards — that's the point of checking before.

If the manifest's file names are still encrypted, step 2 is skipped: use the copy from a Steam
`depotcache` folder, which stores them in the clear.

---

## 4. Apply Goldberg

[SteamAutoCrack](https://github.com/SteamAutoCracks/Steam-auto-crack/releases) does the mechanical
part in one pass. It isn't a separate approach — it drives the same tools this repo documents:
**Steamless** for the SteamStub layer, **gbe_fork** for the Steam API layer, plus its own
Steam-API-Check-Bypass. Those three are listed as its dependencies.

Its readme states .NET 10; if it refuses to start, that's the Desktop Runtime to install.

What to set, on version 3.5.0.6 — it's actively developed, so treat the labels as a description of
intent rather than a script to follow:

- Path: the game folder
- Steam AppID: yours
- Language: whatever you play in
- Enable the steps you want: generate the game info and config, unpack SteamStub, apply Goldberg
- SteamAPICheckBypass Mode: `Disabled`

Hit Start. You end up with a Goldberg `steam_api64.dll`, a `.bak` of the original next to it, and a
`steam_settings\` folder. The game should launch.

That `.bak` is the same thing the [Goldberg guide](running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)
calls `steam_api64_o.dll` — SteamAutoCrack just picks a different suffix. Keep it either way:
it's what `generate_interfaces` needs if you end up redoing the step by hand.

Doing it by hand is covered in that same guide; if the game still won't start, that's the
[Steamless](running/Steamless%20Usage%20Guide.md) case.

> **Which gbe_fork build?** Not one you chose. SteamAutoCrack ships its own copy and updates it on
> its own schedule — "Update gbe_fork" appears in its release notes routinely. That's convenient
> and it's usually current, but it means the binary in your game folder isn't the one you verified.
> For anything involving EOS below, or if you want the version pinned, install
> [gbe_fork](running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) yourself.
>
> It also has a **Restore Crack** function, which is the rollback for everything it did — worth
> knowing before you start undoing things by hand.

---

## 5. Multiplayer

### The game has `EOSSDK-Win64-Shipping.dll`

**First check the store page actually lists multiplayer.** The SDK ships in plenty of single-player
games for save sync or achievements — Hades and Fading Echo both carry it and neither has any
multiplayer at all. A DLL on disk is not a backend.

If it does have multiplayer, its login very likely goes through Epic rather than Steam, and where the
sessions really do run on EOS you end up playing with people who bought the game normally. Rename the
SDK to `EOSSDK-Win64-Shipping.yes`, drop
[eos-proxy](https://github.com/yesyes0649/eos-proxy/releases) in its place under the original name,
launch.

If it doesn't connect, the usual cause is the Steam side: most games want
`GetAuthTicketForWebApi` to return something before they even call EOS. Replace whatever
SteamAutoCrack installed with a current
[gbe_fork](https://github.com/Detanup01/gbe_fork/releases) build, which handles that call — and
check `epic_proxy.log` next to the game executable, which will tell you whether the proxy was ever
reached at all. Details and the full failure table are in the
[EOS Proxy guide](multiplayer/EOS%20Proxy%20Usage%20Guide.md).

A login that succeeds is not multiplayer that works: if the log shows `ResultCode: 0` and the game
still can't reach anyone, the feature you want runs on the publisher's own backend, and nothing
client-side gets past that — see
[the wall](multiplayer/Multiplayer%20Routing.md#the-wall-that-no-client-side-tool-passes).

### Steamworks only

Goldberg gives you LAN, and nothing more. To play with someone who isn't on your network, put
everyone on the same virtual LAN — [ZeroTier](https://www.zerotier.com) or
[Radmin VPN](https://www.radmin-vpn.com).

[Online-Fix](https://online-fix.me/) is the other option and it does work, but its DLLs are
obfuscated. Scan before running, and understand that a clean VirusTotal result on an obfuscated
binary is weak evidence, not proof.

### Anything else

Epic-only titles, EA App, Ubisoft Connect — out of scope. None of these tools touch them.

[Denuvo](other/Denuvo.md) is its own page: it's the one that looks like it should be step 3's problem and
isn't, and it's worth checking for before you start rather than after.

---

## 6. Living with it

- Keep the `.bak` and the `.yes`. They're your two-minute rollback.
- Back up the folder once it works, before you change anything else.
- The folder no longer updates itself — and if you own the game and left it in `steamapps\common\`,
  Steam will update *over* your work. Both cases are covered in
  [Updating a game](game-files/Updating%20a%20Cracked%20Game.md).
- Crash on launch after adding the proxy: pull the proxy out, rename `.yes` back to `.dll`, confirm
  the game still runs, then reintroduce one thing at a time.
- Missing `vcruntime140.dll` → [VC++ redist](https://aka.ms/vs/17/release/vc_redist.x64.exe).
- Anything closed or obfuscated goes through [VirusTotal](https://www.virustotal.com) first.

---

## Links

Research: [SteamDB](https://steamdb.info) · [PCGamingWiki](https://www.pcgamingwiki.com) · [cs.rin.ru](https://cs.rin.ru/)

Tools: [SteamAutoCrack](https://github.com/SteamAutoCracks/Steam-auto-crack) ·
[gbe_fork](https://github.com/Detanup01/gbe_fork) ·
[Goldberg (original)](https://gitlab.com/Mr_Goldberg/goldberg_emulator) ·
[eos-proxy](https://github.com/yesyes0649/eos-proxy) ·
[DepotDownloader](https://github.com/SteamRE/DepotDownloader) ·
[DepotDownloaderMod](https://github.com/SteamAutoCracks/DepotDownloaderMod)

Everything else: [uBlock Origin](https://ublockorigin.com/) · [VirusTotal](https://www.virustotal.com) ·
[ZeroTier](https://www.zerotier.com) · [Radmin VPN](https://www.radmin-vpn.com) ·
[VC++ 2022 redist](https://aka.ms/vs/17/release/vc_redist.x64.exe)
