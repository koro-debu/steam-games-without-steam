# RUNE Steam Emulator — User Guide

Alternative to [Goldberg](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) for running a
game you own without the Steam client. Much simpler to set up — no interface generation — but
also less configurable, and with no upstream at all: new builds (1.0.1.72 in September 2026) only
surface as files inside the RUNE group's own releases, with no changelog and nothing to check them
against.

> **For legal owners only.** Unlike Goldberg, RUNE has no official upstream repository, so there
> is no trustworthy source to point at. Treat any copy you find as unverified and scan it.

---

## What's actually in the package

Worth knowing, because it's the one tool here you can't audit (checked 2026-08-09):

- **`steam_api64.rne` is Valve's real `steam_api64.dll`**, renamed. Signature verifies, 0/71 on
  VirusTotal. RUNE keeps it and forwards to it — that's why you must ship all three files.
- **`steam_api64.dll` is the emulator** — version string `1.0.1.70`, the build the forum calls the
  stable one — and it is packed: two sections named `WUS0`/`WUS1`, one at 7.94 entropy.
- **The packing is plain UPX in disguise**, the same trick CODEX used (RUNE is CODEX's successor, and
  a 2023 cs.rin.ru write-up dissected the CODEX original). The section names `UPX0`/`UPX1` were renamed
  and the `UPX!` marker at offset `0x3E0` was overwritten with the bytes `01 03 03 07` ("1337"), so
  the stock unpacker refuses it. Put the three markers back and the official UPX 5.2.1 tests it OK and
  unpacks it to 2.9 MB (sha256 `621bd15b…ae88472`). Checked here on 2026-10-10 — statically, nothing
  executed.
- **What the unpacked file asks Windows for.** The ordinary import table is what an SDL-based
  controller layer and an overlay need (window, input, GDI, `ShellExecuteW`, `WSAStartup`). The
  interesting functions are resolved at runtime by **hashed name** (the first 8 bytes of the MD5 of
  the function name) so they don't appear as strings. Hashing all 8,208 functions exported by 23
  core Windows DLLs (`ntdll`, `kernel32`, `advapi32`, `ws2_32`, `winhttp`, `wininet`, `urlmon`,
  `crypt32`, `bcrypt`, `user32`, `shell32`…, names taken from Wine's export lists) and searching for
  them finds exactly **13**:
  - `NtCreateFile`, `NtOpenFile`, `NtQueryAttributesFile`, `NtQueryFullAttributesFile`,
    `NtQueryDirectoryFile`, `LdrLoadDll`, `LdrGetDllHandle` — hooks that **hide files and silently
    redirect** the game to the `.rne` original, so integrity checks see Valve's DLL;
  - `WinVerifyTrust` — hooked so signature checks in the process **always pass**;
  - `connect`, `sendto`, `WSAConnect`, `WinHttpOpen`, `WinHttpConnect` — the hooks behind its
    network-blocking option.

  No hashed resolution of anything to download, upload, start processes, read credentials, write the
  registry or touch other processes. The only URLs in the file belong to the copied DigiCert
  certificate chain. That's not a proof — code can be fetched or built in ways a static pass doesn't
  see — but it is no longer "nothing can be said": what it resolves matches what it's for.
- It carries **Valve's version info and a Valve code-signing certificate that does not verify** —
  the signature was copied from the genuine DLL. For an emulator that has to pass as
  `steam_api64.dll` this is by design, not evidence of malware, but it does mean the Properties
  dialog in Windows will lie to you about who wrote it.
- Reputation is the only real evidence in its favour: 2/71 on VirusTotal across ~8000 submissions,
  both hits generic heuristics (`Artemis!`), sandbox verdict clean.
- The copy checked here is sha256 `bde10c56…86c5b71f`. That's the one these
  instructions were written against; nothing certifies where it originally came from.

None of that is a reason to panic — it's a reason to use [gbe_fork](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)
whenever it works, since it's the only one of the two you can actually read the source of.

---

## Installation

1. Copy these three files into the folder that holds the game's `steam_api64.dll` — usually next to
   the executable; on Unreal Engine games, under `Engine\Binaries\ThirdParty\Steamworks\…\Win64\`
   (see the [Goldberg guide](Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md#step-2--back-up-the-original-dll-do-this-first)):

   - `steam_api64.dll`
   - `steam_api64.rne`
   - `steam_emu.ini`

   Back up the game's original `steam_api64.dll` first (rename it to `steam_api64_o.dll`).

   > The `steam_api64.rne` in the package is a copy of Valve's DLL, not *your* game's copy. Since
   > `steam_api64.dll` is a redistributable that barely changes, this normally doesn't matter — but
   > if the game misbehaves, replace the shipped `.rne` with your own original renamed to `.rne`.

2. Open `steam_emu.ini` in a text editor and change **one line**:

   ```ini
   AppId=APPID
   ```

   Replace `APPID` with the game's numeric AppID.

3. Close Steam completely, then launch the game.

### Beyond the one line

The rest of `steam_emu.ini` is optional, and the comments in the file don't say much. What the
cs.rin.ru regulars have worked out (step-by-step guide by *emoris*, January 2026):

| Key | What it's for |
|---|---|
| `AccountId` (`[Settings]`) | Your account in **SteamID3** form — the short number, not the `7656…` SteamID64 (steamid.io converts). Some games name the save folder after it; leave it fixed rather than `0` (random) so a save keeps working. |
| `UserName`, `Language`, `Country` | What the game sees as your name, language and 2-letter country. |
| `Offline=1` / `BlockConnection=1` | Report Steam as offline / block the game's network access. |
| `SelfProtect=0` | Turns off RUNE's self-hiding hooks. Needed for **DLSS** to appear in some games (Dying Light 2 is the known case). |
| `LegacyCallbacks=1` | For stutters or crashes at startup in games that run NVIDIA's `nvngx_update` (reported on Final Fantasy XVI, Le Mans Ultimate, Tempest Rising). |
| `DLCUnlockall` (`[DLC]`) | `1` answers every DLC as owned; listing the IDs is cleaner. `generate_emu_config -cdx` (see [Saves and achievements](../game-files/Saves%20and%20Achievements.md)) writes a ready `[DLC]` section in RUNE's format. |
| `[Controller]` | Native controller support (rumble, deadzones, Nintendo layout, forced glyph type) in recent builds. |

The pinned package is 1.0.1.70 and already ships `SelfProtect=0`. Not every build knows every key —
one that does nothing may simply not exist in your build.

**The "steak" variant.** Since 1.0.1.61 a steamclient flavour circulates as `steakclient64.dll` +
`winmm.dll` + `steak_emu.ini` (same format as `steam_emu.ini`), dropped next to the game's exe. Its
appeal is that the game's original `steam_api64.dll` stays untouched, which helps with games that
check it. Nothing about it has been verified — same caveats as above, more
so.

---

## Finding the AppID

Search the game on [SteamDB](https://steamdb.info/) — the AppID is on the first line of the page.

Example: Stardew Valley → `413150`.

---

## Saves

```text
C:\Users\Public\Documents\Steam\RUNE\<AppID>\
```

---

## Reverting

Delete the three RUNE files from the game folder and restore the original `steam_api64.dll`.
Nothing else is modified.

---

## Doing it automatically

[RUNEAutoCracker](RUNEAutoCracker.md) does this entire page in one pass, and fills in the DLC list —
the part that costs the most time by hand. It has its own page because it needs its own set of
checks: it installs an emulator with no upstream, and it updates itself.

**Confirmed working** on Car Mechanic Simulator 2018, 2026-08-10 — which is the first time anything
on the RUNE path here has been verified by running it rather than by reading files.

---

## Goldberg or RUNE?

| | Goldberg (gbe_fork) | RUNE |
|---|---|---|
| Setup | interface generation required | drop in 3 files, edit 1 line |
| Maintained | yes | builds still appear, but no upstream, no changelog |
| Configurable (saves, DLC, LAN, overlay) | extensively | barely |
| Trustworthy source | official GitHub | none |
| Auditable | source is public | no source; the binary unpacks with UPX and reads statically (above) |
| 32-bit games | `steam_api.dll` from `x86\` | needs a 32-bit RUNE package — the copy checked here is 64-bit only |

Prefer Goldberg. Fall back to RUNE only when a game misbehaves with it.

RUNE has no equivalent of Goldberg's `steam_interfaces.txt` step because it reads the interface
versions straight out of the original DLL it forwards to — that's the whole reason the setup is
three files and one line.
