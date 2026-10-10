# DepotDownloader — Usage Guide

DepotDownloader pulls game files straight from Steam's content servers, without the Steam client
and without a Steam install directory. It's a SteamRE project built on SteamKit2 — the same library
Steam tooling has used for years — and it's a console program, no GUI.

Three things it's genuinely good for:

- **A clean base.** Files downloaded outside `steamapps\common\`, where Steam will never update over
  them and undo your setup.
- **A specific build.** A given manifest instead of "whatever is current", when the current build
  broke something.
- **A subset.** One depot, one platform, or a handful of files, instead of 80 GB.

> **For legal owners only** — Steam hands out depot keys to accounts that own the app, and refuses
> otherwise. That refusal is the whole security model here; this guide doesn't work around it.

---

## Install

Grab the archive for your platform from
[the releases page](https://github.com/SteamRE/DepotDownloader/releases/latest) — on Windows that's
`DepotDownloader-windows-x64.zip`. These builds are self-contained: **nothing to install**, no .NET
runtime needed. (The separate `DepotDownloader-framework.zip` is 2.5 MB and needs the .NET runtime already
installed — .NET 9 for the current 3.4.0 build. You don't want it unless you know you do.)

Extract to e.g. `C:\Tools\DepotDownloader\` and run it from a terminal opened in that folder. The
archive is ~32 MB and unpacks to a single 79 MB `DepotDownloader.exe` — that's the .NET runtime
bundled inside, not a red flag.

Windows users can also `winget install --exact --id SteamRE.DepotDownloader`.

> **If the command line is the obstacle**, [SteamDepotDownloaderGUI](https://github.com/mmvanheusden/SteamDepotDownloaderGUI)
> (GPL-3.0) is a front end over this exact tool, built around the downgrade case: pick a game, pick a
> build, download. It drives the same binary and hits the same limits, including the one below about
> old manifests — a GUI cannot make Steam issue a code it refuses to issue.

---

## The basics

```powershell
./DepotDownloader -app <appid> -dir "C:\Games\MyGame"
```

That downloads the app's current public build for your OS, using an **anonymous** account. Anonymous
only reaches [free and anonymous-accessible apps](https://steamdb.info/sub/17906/) — dedicated
servers, demos, a handful of free games. For anything you bought:

```powershell
./DepotDownloader -app <appid> -dir "C:\Games\MyGame" -username <you> -remember-password
```

The password is asked interactively when you leave `-password` out, which is what you want — no
credential in your shell history. `-remember-password` persists the session so you're not typing a
2FA code on every run.

> **Running it while Steam is open** will disconnect one of the two: they share a LoginID. Pass
> `-loginid <number>` (any 32-bit integer) to run alongside the client.

---

## Downloading a specific depot or build

```powershell
./DepotDownloader -app 730 -depot 731 -manifest 7617088375292372759 -dir "C:\Games\CS"
```

- **`-depot`** — one depot instead of all of them. Games split content into depots per platform,
  per language, sometimes per DLC.
- **`-manifest`** — a specific snapshot of that depot, i.e. a specific build. Requires `-depot`.
  Without it you get the current one for the branch.

Both IDs come from the game's [SteamDB](https://steamdb.info/) page: the *Depots* tab lists the
depots, and each depot's *Manifests* history lists past builds with their manifest IDs and dates.

Other flags worth knowing:

| Flag | What it does |
|---|---|
| `-branch <name>` | download a beta branch instead of `public` (`-branchpassword` if it's locked) |
| `-os windows` / `-osarch 64` | override the platform depots, e.g. pull Windows files from Linux |
| `-validate` | checksum what's already on disk — the repair option |
| `-manifest-only` | download a readable file list instead of the content. Ideal for looking before committing to 40 GB |
| `-filelist list.txt` | download only the listed paths; prefix a line with `regex:` to match patterns |
| `-max-downloads 16` | more parallel chunks. Worth raising on old builds, where the CDN is slow |

---

## Workshop items, without the client

The same tool downloads Steam Workshop content, which is useful when you want a mod's files rather
than a subscription — to read them, to keep a version that still works, or to use them outside the
game's own mod manager.

```powershell
./DepotDownloader -app 730 -pubfile 1885082371
```

- **`-pubfile`** — the **PublishedFileId**, the number at the end of a Workshop item's URL
  (`.../sharedfiles/filedetails/?id=1885082371`). This is the one you'll use.
- **`-ugc`** — the underlying UGC id, if you happen to have that instead. `-pubfile` resolves to it
  for you.

Log in with your own account (`-username`): the Workshop content of a game is served to accounts that
own it. Anonymous downloads only work for the games Valve includes in its anonymous
dedicated-server package (SteamDB sub 17906 lists them) — mostly titles with a dedicated server.

Two things to expect: you get the item's **raw files**, not an installed mod — where they belong is
the game's business, not the downloader's. And a Workshop item is a snapshot; downloading it again
later gets you whatever the author has published by then, so if a specific version matters to you,
keep the copy.

**With a window instead of a command line:**
[Streamline](https://github.com/dane-9/Streamline-Workshop-Downloader) (LGPL-3.0, v2.2.0, August
2026, Windows and Linux) drives SteamCMD the same way — single items, whole collections, or a game's
entire Workshop — and logs in with your account inside SteamCMD rather than storing the password.
Two things to know: it refreshes its list of supported games by scraping SteamDB, and checking
thousands of already-downloaded items at once gets your IP rate-limited by Steam, so use its
*update only* option. Skip the older *WorkshopDL* (end of support in January 2023, built in
Clickteam Fusion, its early versions pulled from third-party mirror sites) and any "online
downloader" website — those work by running shared accounts.

---

## Old builds are not guaranteed

This is the limitation to understand before planning anything around it.

Fetching an old manifest requires a **manifest request code** from Steam, and Steam does not always
issue one. Developers can block downloads of old manifests outright, and when that happens you get
**error 401 / no manifest code returned** no matter how correct your command is. Anonymous logins
hit this far more often — log in with an account that owns the game before concluding a build is
unavailable.

The practical consequence: **a build you already have on disk may be irreplaceable.** Archive
anything you might want later, because "I'll just re-download it" is not something Steam promises.

---

## Common errors

| Message | Meaning |
|---|---|
| `AccessDenied` on a depot | The account doesn't own the app, so Steam won't release the depot key. Not a syntax problem |
| Error 401 / no manifest code | That old manifest can't be fetched — try a real account, otherwise it's blocked upstream |
| Nothing downloads, no error | The depot has no files for your OS/arch. Add `-os windows` or `-all-platforms` |
| Prompted for 2FA every run | Add `-remember-password` |
| Very slow, timeouts on an old build | Normal — cold CDN chunks. Raise `-max-downloads` |

---

## After the download

You have raw game files and no Steam client. To actually run them, that's the
[Steam API layer](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) — and the
[generic guide](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md)
walks the whole path from here to a game that launches.

Note that DepotDownloader gives you a **clean, unmodified** base by definition. That's its main
value for anything in this repo: whatever you add afterwards, you know exactly what was there first.
For a base that came from anywhere else, [`verify_base.py`](verify_base.py) checks it against the
depot's manifest — see [the generic guide](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md#check-that-base-before-you-build-on-it).

---

## Links

- Repository: https://github.com/SteamRE/DepotDownloader
- Releases: https://github.com/SteamRE/DepotDownloader/releases/latest
- Apps available anonymously: https://steamdb.info/sub/17906/
- Depot and manifest IDs: https://steamdb.info/
