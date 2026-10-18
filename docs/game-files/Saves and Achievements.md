# Saves and Achievements Under the Emulator

The moment you swap `steam_api64.dll` for gbe_fork, two things quietly change owner: where your saves
are written, and what happens to achievements. Neither is mentioned when it happens, and the first
one is how people lose a hundred hours.

Read this **before** the switch, not after.

---

## Where saves actually go

Three cases, and which one you're in depends entirely on how the game was written.

| The game writes saves… | What the switch changes |
|---|---|
| To its own folder in `Documents\` or `%APPDATA%\` | **Nothing.** The game never asked Steam, so the emulator isn't involved |
| Through Steam Cloud / Remote Storage | **Everything.** Those calls now land in gbe_fork's own folder, and your existing saves are invisible to the game |
| Into the game's install folder | Nothing, unless you also replaced the folder |

A fourth case is easy to miss: **the game picks between those depending on where it is installed.**
*A Dance of Fire and Ice* (Unity; read in its code, build 24397494) writes `data.sav` and
`custom_data.sav` into `<game folder>\User\` **only when the game folder sits inside a
`steamapps\common\` folder**. Anywhere else — your desktop, a games drive — it writes to
`%USERPROFILE%\AppData\LocalLow\7th Beat Games\A Dance of Fire and Ice\` instead, and starts from a
blank save. So moving your copy out of the Steam library looks like losing your progress. Two fixes:
copy the two `.sav` files into the folder it now uses, or keep the copy under a path ending in
`steamapps\common\A Dance of Fire and Ice` (any drive, no Steam needed — only the folder names
matter), and the saves stay next to the game. Unity games in general default to that `LocalLow`
folder; it's the "own folder" case of the first row.

gbe_fork's location, on Windows:

```text
%APPDATA%\GSE Saves\
```

Inside, the emulator keeps a global `settings\` folder — that's where `custom_broadcasts.txt`, the
account avatar and the overlay sounds live — next to per-game data. Two settings in
`steam_settings\configs.user.ini` change where all of it goes:

```ini
[user::saves]
; keep everything inside the game folder instead — fully portable
local_save_path=./
; or just rename the base folder
saves_folder_name=GSE Saves
```

`local_save_path` makes the emulator **ignore the global folder entirely**. That's the option to use
if you keep games on an external drive — and the one that will bite you at update time, since your
saves then live inside the folder you're about to overwrite. See
[Updating a game](Updating%20a%20Cracked%20Game.md).

---

## Bringing your existing saves across

Only needed for the Steam Cloud case above. Do it while you still have a working Steam install.

1. Find your Steam save folder:
   ```text
   <Steam>\userdata\<your account id>\<AppID>\
   ```
   Inside, `remote\` is what the game wrote through Steam Cloud.
2. Run the game **once** under the emulator, save in-game, and quit. That creates the game's own
   folder under `%APPDATA%\GSE Saves\`, with the structure the emulator expects.
3. Compare the two trees and copy your real save files into the matching place. Copy — don't move,
   until you've confirmed the game loads them.

Doing it in that order matters: let the emulator create its layout first, then fill it. Guessing the
structure beforehand is how you end up with files in a folder nothing reads.

**Some games tie the save to your SteamID** — the save folder is named after it, or the file is
encrypted with it (Dark Souls III is the usual example). Copied under the emulator's random ID, such
a save is ignored or rejected. Give the emulator *your* ID: set `account_steamid=` in
`steam_settings\configs.user.ini` to your SteamID64 (the `7656…` number). You don't need a website to
find it — open any `<Steam>\steamapps\appmanifest_*.acf` in a text editor: the `LastOwner` value is
your SteamID64. Games that only need the ID for a while and then something else have
`alt_steamid` / `alt_steamid_count` in the same file. One catch, found in 2019 on Nioh and Senran Kagura and
still true: some games store the 32-bit account part of the ID as a *signed* number, and an account
ID above 2,147,483,647 turns negative and crashes them — if a game refuses an ID that works
elsewhere, try a lower one (and keep the save trick for games that really need *yours*).

> **Steam Cloud does not sync back.** Progress you make under the emulator stays local. If you later
> return to the real Steam version, that progress won't be there — and the reverse, Steam's cloud
> overwriting your local saves, is worth guarding against by keeping a copy outside both.

---

## Keeping the saves next to the game

A cracked copy is easier to back up, move or delete when its saves live in its own folder — say
`<game>\Saves\` — instead of somewhere under `%APPDATA%`. How you get there depends on who writes the
save (the table at the top).

**Through the emulator** (Steam Cloud games): `local_save_path` in `steam_settings\configs.user.ini`.
Two details decide whether it works:

- **The path is relative to the folder of the emulator's DLL**, not to the exe. For a Unity game the
  DLL sits in `<Game>_Data\Plugins\x86_64\`, so the game's root is three levels up:
  ```ini
  [user::saves]
  local_save_path=../../../Saves/Goldberg
  ```
- **Pin the SteamID in the same file.** With `local_save_path` set, the emulator ignores the global
  `GSE Saves\settings\` folder — including the ID it generated the first time. Without
  `account_steamid=` under `[user::general]` it may draw a new one, and a game that files saves by
  SteamID then starts blank. Use the ID the game was already using (the name of its save folder, if it
  makes one per SteamID). Then copy `GSE Saves\<appid>\` into the new folder.

**By the game itself, outside the install** (Unity's `%USERPROFILE%\AppData\LocalLow\<Company>\<Product>\`,
`Saved Games`, `Documents\My Games`…): first check whether the game picks its folder from its own
location or a setting (the *A Dance of Fire and Ice* case above) — if it does, use that. Otherwise the
game has no option to change, but Windows does: a **directory junction** from the folder the game
expects to the one next to it. `mklink /J` needs no administrator rights, and `rmdir` without `/s` on
a junction removes only the link, never the files behind it. Wrapping it in a launcher that sets the
junction up for the session and removes it afterwards keeps the real install (if you also play it
through Steam) untouched:

```bat
@echo off
rem Starts the game with its saves in the "Saves" folder next to it.
setlocal
set "L=%USERPROFILE%\AppData\LocalLow\Company\Product"
set "S=%~dp0Saves"
set "G=%~dp0"
for %%I in ("%L%") do (set "P=%%~dpI" & set "B=%%~nxI")
if not exist "%S%" mkdir "%S%"
if not exist "%P%" mkdir "%P%"
rem a link left behind by a crashed session: remove the link only
dir /AL /B "%P%" 2>nul | findstr /X /I /L /C:"%B%" >nul && rmdir "%L%"
rem a real folder (the Steam version's saves): set aside as _o, put back at the end
if exist "%L%\" (
  if exist "%L%_o\" ( echo "%L%_o" already exists, nothing touched. & pause & exit /b 1 )
  ren "%L%" "%B%_o"
)
mklink /J "%L%" "%S%" >nul
dir /AL /B "%P%" 2>nul | findstr /X /I /L /C:"%B%" >nul || goto failed
cd /d "%~dp0"
start "" /wait "%~dp0Game.exe"
rem some games restart themselves in a new process: wait until nothing from this folder runs
:wait
powershell -NoProfile -Command "if (Get-Process | Where-Object { $_.Path -and $_.Path.StartsWith($env:G, [StringComparison]::OrdinalIgnoreCase) }) { exit 1 }" >nul 2>&1
if errorlevel 1 ( timeout /t 5 /nobreak >nul & goto wait )
rmdir "%L%"
if exist "%L%_o\" ren "%L%_o" "%B%"
exit /b 0
:failed
echo Could not create the link to "%S%": the game was not started.
if not exist "%L%\" if exist "%L%_o\" ren "%L%_o" "%B%"
pause
exit /b 1
```

Set `L` to the game's folder and `Game.exe` to its exe, save it as `Start <game>.cmd` in the game
folder, and point your shortcut at it (*Run: Minimized* hides the console). Before the first run,
**copy the existing saves into `Saves\`** with the game closed — otherwise the first session shows an
empty folder and the old saves sit in `_o` until the end. Rules that follow from how it works:

- **Always start the game through the launcher.** Started from its exe, the game writes to the
  normal folder again.
- **A save folder already called `<name>_o`** stops the launcher: it would otherwise overwrite it.
- **Batch files are read in the console's code page**: a path with accented characters must be
  saved in that encoding (OEM, e.g. 850), not UTF-8.
- **Some games write the SteamID inside the save file too**, not just in the folder name — *How to
  Fish* (Unity) keeps it in `Players[].SteamID` of its JSON save. Moving such a save to another ID
  means editing the file, not just renaming the folder; pinning `account_steamid` avoids the problem.
- **Updating the game** later: your saves are now inside the folder you'd overwrite — see
  [Updating a game](Updating%20a%20Cracked%20Game.md).

Both methods can be combined: the emulator's files in `Saves\Goldberg\`, the game's own in `Saves\`.

---

## Achievements: two halves that people confuse

An achievement needs a **definition** (what exists, what it's called) and a **state** (whether you
unlocked it). Steam normally provides both. Under the emulator they come from different places, and
missing the first half is why "achievements don't work" is usually a configuration gap, not a bug.

**Definitions** come from `steam_settings\achievements.json` — a file that does not exist unless you
create it. Without it the emulator has nothing to unlock, and the game sees a title with zero
achievements.

**Counter achievements need a second file.** "Collect 50 …", "finish every chapter" — anything driven
by a stat — only ever unlocks if `steam_settings\stats.json` declares those stats; the emulator
silently ignores a stat it doesn't know, so the threshold is never reached. The generators below
write it alongside `achievements.json`. Progress made *before* the file existed was never recorded:
it starts counting from the moment you add it.

Generating it needs a third-party tool, and the situation there is worth knowing before you go
looking. The release README still tells you to use `generate_emu_config`; that tool was moved out of
gbe_fork into [gbe_fork_tools](https://github.com/Detanup01/gbe_fork_tools) and renamed
**`generate_emu_config_old`**, where its author states he has no plan to rebuild it and suggests
using anything equivalent.

**Someone else did keep it alive.** [gse_fork_tools](https://github.com/alex47exe/gse_fork_tools)
(alex47exe, LGPL-3.0) carries an overhauled `generate_emu_config_old` — despite the name, the
*maintained* one: batch generation, invalid AppIDs skipped instead of crashing the run, DLC and
cloud-save sections parsed properly, and upstream changes merged in (latest on 2026-08-27). It also
writes the files Achievement Watcher reads. What to know before using it:

- **It's a Steam client, and it asks for a login.** It talks to Steam directly (through the author's
  fork of the `steam` Python library — nothing goes to a third-party server), and you can run it
  **anonymously**, which gets you less data. Try anonymous first. If you need more, use a secondary
  account rather than your main one, and never leave a `my_login.txt` next to it: that file is your
  password in plain text.
- **The binary lags the source.** The last packaged release is `2026_02_16`
  (`gen_emu_cfg-Windows-Release.7z`, sha256 `17a64b30…5c23a0`, 4/61 on VirusTotal, all generic
  heuristics on a PyInstaller bundle). The fixes since then are only in the source — run the `.py`
  if you hit one of them.
- **Same author, other repo:** [gse_fork](https://github.com/alex47exe/gse_fork) is his own fork of
  the emulator. Its last build is from 2026-02-16 and its work since is mostly the overlay and a
  ReShade add-on, so this repo stays on gbe_fork. The generator works with both.

[GSE-Generator](https://github.com/brunolee-GIT/GSE-Generator) (MIT, v1.0.5, October 2024) is still
the simpler alternative and the one in the
[Goldberg guide](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)'s requirements
table — but it hasn't moved in two years.

If you can't or won't log in to Steam at all, [GB-ADB](https://github.com/0P3N50URC3-F0R3V3R/GB-ADB)
is a pre-generated database of achievement files for gbe_fork, browsable on its GitHub page. It's a
third-party scrape — about 2 % of entries in the wrong language, some labelled `Unknown_Game`, and the online copy
frozen at roughly 15,000 games when the repository hit GitHub's size limit. A fallback, not a first choice: files you generate yourself match your build.

**State** is stored per-AppID under `GSE Saves\`, and it's local. It is not on your Steam profile and
never will be — no amount of unlocking under the emulator touches your account. That cuts both ways:
nothing to gain, and nothing to lose.

The same file can carry an `unlock_percentage` per achievement (0.0–100.0, the global unlock rate);
when it's there, the emulator's overlay shows it in the achievement list.

**You won't see notifications** unless the experimental overlay is enabled — it's off by default, see
[Common configuration](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md#overlay).
Which brings us to the alternative.

---

## Achievement Watcher

[Achievement Watcher](https://github.com/xan105/Achievement-Watcher) reads the achievement files
emulators leave behind and gives you back what the overlay doesn't: toast notifications on unlock, a
browsable list with real names and icons, playtime tracking.

### Use Achievement Watcher Next instead

The original stopped in 2022 (details below). Its successor is
[Achievement Watcher Next](https://github.com/Shirowwww/Achievement-Watcher-Next) — LGPL-3.0, a fork
of a fork of xan105's, **v3.11.2 on 2026-10-09** and releasing every few days. It fixes both problems
the original has with gbe_fork:

- **No Steam Web API key.** Achievement lists come from public endpoints and are cached locally.
- **It finds `GSE Saves` by itself.** *Settings → Folders → Smart Find* scans your drives instead of
  trusting a fixed list, and a per-game health panel tells you *why* a game sits at 0% — usually the
  missing `achievements.json` above.

It also imports an existing Achievement Watcher setup on first launch, without modifying it.

Worth knowing:

- **Reading is read-only; the "repair" buttons are not.** They modify game files, after a
  confirmation and with a backup. Treat them like any other tool writing into a game folder — the
  [`_o` rule](../running/Steamless%20Usage%20Guide.md) still applies to what you keep.
- **Account connections are optional — leave Steam unconnected.** It can sign in to Steam, Epic or
  Xbox to show unlocks from other PCs. Nothing here needs that.
- **Use 3.10.9 or later.** Before it, an ordinary library scan rewrote `configs.app.ini`,
  `configs.main.ini` and `configs.user.ini` in every gbe_fork game it found — even with *Automatically
  fix newly detected games* off — and the "backups" it kept were taken after the change. The author
  acknowledged it as a bug and fixed it; just don't run an older build.
- **3.11.0 tripped Kaspersky** (a behaviour detection when the app ran, and ESET/Rising on the
  installer as *CaptureScreen*): its screenshot feature compiled a capture program into `%TEMP%`
  with `csc.exe`, and notifications went through compiled PowerShell. 3.11.1 and 3.11.2 removed both.
  If your antivirus reacted to 3.11.0, that is the explanation — update rather than whitelist.
- **Self-signed.** Installers carry the project's own `CN=Shirow` certificate, so SmartScreen will
  complain; the updater only accepts updates signed with that exact certificate. Download from the
  [releases page](https://github.com/Shirowwww/Achievement-Watcher-Next/releases) only. The 3.11.2
  installer was 0/53 on VirusTotal on 2026-10-10 — on a single submission, so that's no history yet,
  just no detection.

### The other one people use: JokerVerse's *Achievements*

[Achievements](https://github.com/PSerban93/Achievements) (PSerban93, MIT, v1.3.0, September 2026)
is not an Achievement Watcher fork but a rewrite, and on cs.rin.ru it has become the community
default. It's worth knowing what it asks for before you hand it anything: it can run the config
generator **with your Steam username and password**, link Epic and Microsoft accounts, install a
global keyboard hook, and scrape SteamDB with its own headless Chromium when you give it no API key.
None of that is needed to *watch* a `GSE Saves` folder — use it read-only, like AW Next, and skip the
logins. (darktakayanagi's AW 2.0 fork, the other name you'll see, has had no release since January
2026.)

### Notifications that never show up

The same causes, whichever app you use — collected over seven years of that thread:

- **Exclusive full screen never shows a toast.** Play borderless or windowed.
- **Focus Assist eats them.** Windows turns on automatic rules for games and full-screen apps that
  switch to "alarms only" — disable those rules, not just Focus Assist itself.
- **The toasts go through the Xbox Game Bar** identity. Windows "N" editions, LTSC and debloated
  installs that removed it break notifications; repairing Game Bar is the fix.
- **A folder you added has its notifications off** until you click its bell icon.
- **A game only appears once the emulator has written something** — gbe_fork creates
  `GSE Saves\<appid>` on the first unlock. Creating the empty folder yourself makes it show.
- **To be notified again for an achievement**, delete the app's cache for that game
  (`steam_cache\data\<appid>.db`) as well as the emulator's file.
- Some games only fire achievements when started with their Steam launch arguments (Days Gone's
  `-Steamworks -Installed`, Satisfactory's `-NO_EOS_OVERLAY`) — see the
  [Goldberg guide](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md#launching).
- RUNE often leaves its `achievements.ini` empty and doesn't do stat-based achievements; nothing to
  watch there.

The rest of this section is about the original, for anyone staying on it.

### The original (xan105, 1.6.8)

**It does not find gbe_fork out of the box, and that trips everyone.** Its default scan list includes
`%appdata%\Goldberg SteamEmu Saves` — the folder name used by the *original* Mr_Goldberg emulator.
gbe_fork writes to `%APPDATA%\GSE Saves`, which isn't on that list. Two ways out:

1. **Add the folder in the app** (preferred). It accepts any directory whose children are AppID
   folders — so point it at `GSE Saves\` once the game has run at least once and you can see the
   per-game folders it created. Then **click the bell icon next to it**: without that you get the
   list, but no notifications.
2. **Rename on the emulator side**: set `saves_folder_name=Goldberg SteamEmu Saves` in
   `configs.user.ini` and it lands where the app already looks.

Two caveats before you install it:

- **You need your own Steam Web API key.** The project's cache server was shut down, so the app can't
  resolve achievement names and icons without one. Get a key at
  [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey) and paste it into
  *Settings → Advanced*.
- **Last release is 1.6.8, July 2022.** It still works — the file formats it parses haven't moved —
  but nobody is fixing it if a future gbe_fork changes its layout. Its author ran the cache server out
  of his own pocket and shut it down in November 2022; that's the server everyone still mentions.
- **Its watchdog listens on port 8082 on every network interface** (a websocket, `0.0.0.0`), which
  also collides with Hamachi; and if the watchdog decides the game isn't running because the schema
  names the wrong `binary`, set `checkIfProcessIsRunning=false` in its options.
- **`logs\notification.log` prints your Steam Web API key in clear text** — redact it before posting
  a log anywhere. (A key registered for the domain `127.0.0.1` works fine.)

---

## Backing them up without doing it by hand

Copying `GSE Saves\` somewhere safe works, and you will forget to do it. [Ludusavi](https://github.com/mtkennerly/ludusavi)
(MIT, actively maintained) is the tool for this: it knows where thousands of games keep their saves,
backs them up on a schedule, and restores them per game.

Out of the box it only knows *real* save locations, not emulator ones. A community manifest fills
that gap — it adds `%APPDATA%\GSE Saves`, the original Goldberg folder and other emulator paths:

1. Ludusavi → **Other** tab → *Manifest* section, input mode **URL**
2. Add `https://raw.githubusercontent.com/DogancanYr/ludusavi-piracy-manifest/refs/heads/main/Piracy-manifest.yaml`
3. Click the reload button; a *Checked:* timestamp means it took

The manifest is a YAML file with no licence and very few users, so read it before adding it — it's a
list of paths, which takes a minute. Ludusavi itself is the part that matters and that one is
mainstream.

---

## Quick answers

| Question | Answer |
|---|---|
| Will I lose my saves by switching? | Only if the game used Steam Cloud — and only if you don't copy them first |
| I copied my save and the game ignores it | It's tied to your SteamID — set `account_steamid` to the `LastOwner` value of an `appmanifest_*.acf` |
| Do emulated achievements show on my profile? | No. Local only, always |
| Achievements unlock, except the "collect N" ones | No `stats.json` in `steam_settings` — counters aren't tracked without it |
| Why does the game show zero achievements? | No `achievements.json` in `steam_settings` — generate it; the maintained `generate_emu_config` lives in [gse_fork_tools](https://github.com/alex47exe/gse_fork_tools) |
| Why no unlock notification? | The overlay is off by default; or use Achievement Watcher Next |
| Achievement Watcher sees nothing | The original scans `Goldberg SteamEmu Saves`, not `GSE Saves`: add the folder, then click the bell. AW Next finds it with *Smart Find* |
| Can the saves live in the game folder? | Emulator saves: `local_save_path` (relative to the DLL's folder) + `account_steamid`. The game's own: a junction launcher — see [Keeping the saves next to the game](#keeping-the-saves-next-to-the-game) |
| Can I sync progress back to Steam afterwards? | No |
