# Steamless — Usage Guide

Steamless removes the **SteamStub** DRM wrapper from a game executable, leaving a plain `.exe`
that a debugger, disassembler or trainer can work with — and that starts without Steam.

It only handles SteamStub. It does nothing about VMProtect, EOS, EA App or Ubisoft Connect — and
nothing about [Denuvo](../other/Denuvo.md), which is the one people most often expect it to solve.

> **For legal owners only.** Personal modding, technical analysis and offline play of a game you
> bought. Distributing an unpacked executable is a different thing entirely, and illegal.
> Note that bypassing DRM can be unlawful even for personal use in some jurisdictions
> (DMCA in the US, EUCD in the EU).

---

## Do you actually need it?

If the [README](../index.md) sent you here, yes. Otherwise the short version: try
[Goldberg](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) first, and only reach for
Steamless when the game still won't launch, still says *"Steam must be running"*, or when you want
to attach a debugger to a binary that isn't wrapped.

### How to tell whether a game has SteamStub

- **Run Steamless on it** — it reports the variant, or says the file isn't packed.
- **Check [PCGamingWiki](https://www.pcgamingwiki.com/)** — the DRM section names SteamStub when
  it's present.
- **Symptom:** Goldberg installed but the game still demands Steam → probably SteamStub.
- **Look without running anything:** open the exe in a PE viewer (CFF Explorer, PE-bear) and list
  its sections. A SteamStub-wrapped file carries a section named **`.bind`**, normally the last
  one; when another protection (SecuROM, Denuvo) is stacked on top it can sit elsewhere.

**Why an emulator can't simply answer the stub.** SteamStub doesn't ask `steam_api` whether you own
the game — it asks the running Steam client for an **ownership ticket** signed by Valve (SteamID,
AppID, owned DLC, a validity window of a few weeks) and checks the signature. Producing that needs
Valve's private key, so no emulator can fake it: the stub has to be removed from the file, which is
what Steamless does.

**What Steamless doesn't cover:**

- **CEG** (Custom Executable Generation) is a different, older Steam DRM — a per-account build of the
  exe. A game that drops a `<name>.STEAMSTART` file next to itself and refuses to start is a CEG
  title; Steamless and the regular emulators don't handle it, and this repo has no auditable answer
  for it.
- **Linux executables.** Steamless is Windows-only. For a native Linux binary wrapped in SteamStub
  3.0/3.1, [pyUnstub](https://gitlab.com/sektour/steamstub_scripts) is a small Python
  reimplementation of the same unpacking (CC BY-NC-SA 4.0, last updated 2021, four stars — read it before you trust it;
  it's short).

---

## Download

Official repository: https://github.com/atom0s/Steamless

Take the latest release archive from **Releases** — the file is named
`Steamless.vX.X.X.X.-.by.atom0s.zip` — and extract it to e.g. `C:\Tools\Steamless\`.

> Download from atom0s's GitHub and nowhere else. Copies from other sources are a known malware
> vector; check hashes on [VirusTotal](https://www.virustotal.com/) if in doubt.

---

## Before you start

### Antivirus

Steamless rewrites PE structures, which is textbook malware behaviour, so every engine flags it:

- Windows Defender → `HackTool:Win32/Steamless`
- Malwarebytes → `PUP.Optional.Steamless`
- Avast / AVG → `Win32:Steamless-A [PUP]`

Add `C:\Tools\Steamless\` to your exclusions. The official build is safe.

### Back up the executable — mandatory

Copy the game's main `.exe` somewhere outside the game folder, or rename it to **`Game_o.exe`**
(the name used everywhere else in this guide). Unpacking can produce a corrupted binary, especially
with experimental features enabled, and this backup is your only way back short of re-downloading
the game.

> **Naming, across this repo:** a file you keep because it's the original gets `_o` appended before
> its extension — `Game_o.exe`, `steam_api64_o.dll`. It's not decoration: SmokeAPI *requires* exactly
> that name in proxy mode, so the convention and the tooling agree.
>
> Two names are imposed and must not be changed: eos-proxy loads `EOSSDK-Win64-Shipping.yes` by that
> exact name, hardcoded.
> [SteamAutoCrack](../Generic%20Guide%20-%20Clean%20Base%20%2B%20Safe%20Crack%20%2B%20Multiplayer.md)
> writes `.bak` when it does the DLL swap for you — same file, its own suffix. Rename it or leave
> it, but don't delete it.

---

## Unpacking

1. Right-click `Steamless.exe` → **Run as administrator** (needed for write access to the game
   folder).
2. Load the executable, either way:
   - **drag and drop** the game `.exe` onto the Steamless window, or
   - click **…** next to *Select File To Unpack* and browse to it.
3. Leave the options at their defaults:

   | Option | Default | Meaning |
   |---|---|---|
   | Verbose Output | ☑ | detailed log — keep it on |
   | Keep Bind Section | ☐ | retains the `.bind` section |
   | Dump Payload To Disk | ☐ | advanced |
   | Dump SteamDRMP.dll To Disk | ☐ | advanced |
   | Use Experimental Features | ☐ | only as a last resort |
   | Don't Realign Sections | ☑ | keep |
   | Zero DOS Stub Data | ☑ | keep |
   | Recalculate File Checksum | ☑ | keep |

4. Click **Unpack File** and read the log.

---

## Reading the result

### SteamStub found and removed

```text
[Steamless] SteamStub Variant X.X detected
[Steamless] Unpacking in progress...
[Steamless] Successfully unpacked file!
[Steamless] File written to disk: Game.unpacked.exe
```

Then, in the game folder:

1. Rename the original `Game.exe` → `Game_o.exe`.
2. Rename `Game.unpacked.exe` → `Game.exe`.
3. Launch and test.

### No SteamStub — the file isn't packed

```text
[Steamless] This file does not appear to be packed with SteamStub!
[Steamless] File missing expected .bind section!
[Steamless] Failed to unpack file.
```

Good news, not an error: the executable is already clean. Nothing to do here — use Goldberg
alone.

### Unpacking error

```text
[Steamless] An error occurred during unpacking
[Steamless] Failed to unpack file.
```

Usually a heavier protection ([Denuvo](../other/Denuvo.md), VMProtect), a corrupted file, or an unsupported
SteamStub variant.

1. Restore your backup.
2. Retry once with **Use Experimental Features** ticked (risky).
3. If that fails, Steamless doesn't support this game. Stop there.

---

## Combining with Goldberg

The two are complementary — Steamless deals with the executable, Goldberg with the API:

| Tool | Handles | Analogy |
|---|---|---|
| Steamless | SteamStub wrapper on the `.exe` | removes the bouncer at the door |
| Goldberg | `steam_api64.dll` calls | hands out a local access badge |

Unpacking alone is usually **not** enough: the game still calls into the Steam API and will crash
without an emulator in place.

1. Unpack the executable with Steamless, and swap in the `.unpacked.exe`.
2. Install Goldberg — DLL, `steam_settings\`, `steam_appid.txt`, `steam_interfaces.txt`
   (see the [Goldberg guide](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)).
3. Launch.

Resulting layout:

```text
<game folder>\
├── Game.exe                 ← unpacked, SteamStub removed
├── Game_o.exe               ← original, keep it
├── steam_api64.dll          ← Goldberg
├── steam_api64_o.dll        ← original Steam DLL, keep it
└── steam_settings\
    ├── steam_appid.txt
    └── steam_interfaces.txt
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Crashes after unpacking | The Steam API is still missing | Install Goldberg: DLL + `steam_settings\` + correct AppID |
| Steamless finds no SteamStub | The game doesn't use it | Normal — use Goldberg alone |
| Unpacked file is corrupted | Bad unpack | Restore `Game_o.exe`, retry with experimental features, else give up |
| Unpacked exe starts, then the game complains it was modified or quits | It checks its own file size or sections | Restore, unpack again with **Keep Bind Section** ticked — removing `.bind` is exactly what such checks notice |
| "No SteamStub" on an Unreal game | You unpacked the launcher stub | Unpack `<Game>\Binaries\Win64\<Game>-Win64-Shipping.exe`, the real executable |
| SteamStub v1 / variant not supported | Very old games (Max Payne, DOOM 3, BioShock) or a stub wrapped in another packer | Steamless doesn't handle those; see below |
| Antivirus deletes Steamless | False positive | Exclude `C:\Tools\Steamless\`, re-download from the official GitHub |

---

### When Steamless can't do it

gbe_fork's **experimental steamclient** package ships an `extra_dlls` folder with a DLL that patches
SteamStub **in memory at startup** instead of rewriting the exe — upstream calls it "not a complete
solution, just a different method", and warns it must be injected at startup only, never put in
`steam_settings\load_dlls\` (huge FPS drop). It's in gbe_fork's source like the rest of it.

And use atom0s' own releases: he asked people explicitly not to pass around third-party builds of
Steamless — and download the release archive, not GitHub's *Source code* zip, which has no plugins
and unpacks nothing.

---

## Quick reference

1. Download from the official GitHub.
2. **Back up the `.exe`.**
3. Run Steamless as administrator.
4. Drag the game `.exe` in → **Unpack File**.
5. On success, swap `.unpacked.exe` in for the original.
6. Add Goldberg (`steam_api64.dll` + `steam_settings\`).
7. Test.

If Steamless says *not packed with SteamStub*, the game doesn't need it — Goldberg alone.

---

## Links

- Repository: https://github.com/atom0s/Steamless
- Author: http://www.atom0s.com/
- DRM lookup: https://www.pcgamingwiki.com/
- Goldberg: https://github.com/Detanup01/gbe_fork
- AppIDs: https://steamdb.info/
