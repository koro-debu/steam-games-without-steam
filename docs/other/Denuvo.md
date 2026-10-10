# Denuvo — What You Can and Can't Do

Denuvo comes up constantly, and every other guide here dismisses it in half a line. This page is
that half-line expanded: how to recognise it, what the tools here can and can't do with it, and
what's actually left to a legitimate owner.

**Nothing here removes Denuvo** — no open-source tool does, and this page will not point you at the
groups who defeat it title by title. But for a game **you own**, removing it isn't the only way to
play without the client: Denuvo checks ownership with a ticket that your own Steam account can
produce, and gbe_fork can hand that ticket to the game.
[That has its own section below](#running-a-denuvo-game-you-own-without-the-steam-client).
Around it: how to spot Denuvo early, why the rest of the repo doesn't apply, and — since the
hypervisor bypasses appeared — [what those cost](#hypervisor-bypasses--what-they-cost) before you pay it.

---

## What it is, and what it isn't

Denuvo Anti-Tamper is not a wrapper around the executable — that's SteamStub, and
[Steamless](../running/Steamless%20Usage%20Guide.md) handles that. Denuvo is *inside* the executable: parts of
the game's own code are transformed and virtualised, licence checks are woven through them, and the
whole thing verifies its own integrity while it runs.

The practical difference:

| | SteamStub | Denuvo |
|---|---|---|
| What it does | Wraps the `.exe`, unwraps it at launch | Rewrites the game's code and checks itself continuously |
| Where the check lives | Around the binary | Inside the binary, in code you can't read |
| Tooling | Open-source unpacker (Steamless) | None public that removes it |
| Removable by you | Yes, in a click | No — but an owner can [satisfy its check](#running-a-denuvo-game-you-own-without-the-steam-client) |

It is also **not** Steam DRM. A game can ship Denuvo and Steamworks together; they're separate
problems, and the tools here only ever addressed the second one.

### Denuvo is not the only one

Two smaller anti-tamper systems turn up on Steam and behave the same way from your side — the
executable is protected, nothing in this repo applies, and the store notice is where they're
declared. Both were read straight off Steam on 2026-08-10:

| System | Seen on | What Steam says |
|---|---|---|
| **Valeroa** | *City Patrol: Police* ([789890](https://store.steampowered.com/app/789890/)) | "Valeroa Anti-Tamper" |
| unnamed anti-tamper | *Dead Man's Diary* ([1808700](https://store.steampowered.com/app/1808700/)) | "Anti-tamper — 5 activations per 24 hours" |

**Aderow** is a third, and the one most often reported as removed. Treat any of these the way you'd
treat Denuvo: check the store notice for the current build, because these get dropped too.

---

## Recognising it before you start

| Where | What you're looking for |
|---|---|
| Steam store page | The notice in the right column: *"Requires 3rd-Party DRM: Denuvo Anti-tamper"*. Publishers are obliged to declare it |
| [SteamDB](https://steamdb.info/) | The DRM notice on the app page, and its history — that history is how you spot a removal |
| [PCGamingWiki](https://www.pcgamingwiki.com/) | The *DRM* row of the infobox, usually with the removal date if there was one |
| The game folder | A main executable far larger than the game's other binaries, sometimes by tens of megabytes |
| [Steamless](../running/Steamless%20Usage%20Guide.md) | It reports *"does not appear to be packed with SteamStub"*. That's Steamless working correctly, not failing |

Check the store page first. Ninety seconds there beats an evening of unpacking that was never going
to work.

This repo keeps [its own list](../lists/Denuvo.md), built from PCGamingWiki's structured data and
then re-checked game by game against Steam's declaration. It exists mainly to be checked before you
start, but the interesting column is the third one: **155 games where Denuvo was removed**.

Community "blocked games" lists circulate for the same purpose, and they go stale — measurably. Of
the 246 entries with a usable AppID in our own pull (October 2026), **56 no longer declare Denuvo on
Steam** — 23% drift in a list that looks authoritative. Any such list is a snapshot; the store notice is
per-game, current, and comes from the publisher.

---

## Running a Denuvo game you own without the Steam client

Denuvo doesn't care whether the Steam *client* is running. What it checks is proof of ownership: an
**EncryptedAppTicket**, a short-lived ticket Steam issues to a logged-in account for one AppID. On a
normal launch the client fetches it. A small open-source tool can fetch the same ticket from **your**
account ahead of time, and [gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)
can present it to the game in the client's place.

Nothing is cracked: the executable stays untouched, Denuvo still runs, and the ticket is a genuine
one for an account that owns the game. That's also why this only ever works for games you own.

Everything below comes from two documents: the README of
[`denuvosanctuary/steam-ticket-generator`](https://github.com/denuvosanctuary/steam-ticket-generator)
(LGPL-3.0, source public) and gbe_fork's own `configs.user.EXAMPLE.ini`.

### What you need

| | |
|---|---|
| **Your own Steam account, owning the game** | The ticket is issued to whichever account is logged in. Not a family-shared copy — [rule 5](../index.md#five-rules-that-apply-to-everything-here) applies twice here |
| **The Steam client, once** | Installed and logged in to that account while you generate the ticket. After that it can be closed |
| **steam-ticket-generator** | Build it from source (`cargo build --release` → `target/release/steam_ticket_generator.exe`), or take the Windows / Linux build from its [Releases](https://github.com/denuvosanctuary/steam-ticket-generator/releases) |
| **`steam_api64.dll` next to the generator** | It talks to the local client through it. The release builds include it; otherwise take it from the [Steamworks SDK](https://partner.steamgames.com/doc/sdk), **version 1.62 or later**. The Linux release ships `libsteam_api.so` |
| **gbe_fork already working on the game** | Set up exactly as in the [Goldberg guide](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md). This section only adds two lines to it |

### Steps

1. **Open Steam and log in** with the account that owns the game.
2. **Run the generator** and type the game's AppID when it asks. It uses the account currently logged
   in and prints two things: that account's **SteamID** and the **ticket**, in base64.
3. **Put both in gbe_fork's `configs.user.ini`**, under `[user::general]`:

   ```ini
   [user::general]
   account_steamid=YOUR_STEAM_ID
   ticket=BASE64_ENCODED_TICKET
   ```

   That's the same `steam_settings\configs.user.ini` the Goldberg guide already has you edit, next to
   the emulator DLL. Paste the ticket as a single line, exactly as printed.
4. **Launch the game — within 30 minutes** of step 2 (see below). The Steam client can be closed by
   then; gbe_fork is what the game talks to.

### Where it goes wrong

- **The SteamID has to be your real one.** The generator's README is explicit that Denuvo games need
  *"the correct steam account id in the steam emulator settings"* — the ticket belongs to one account,
  and the emulator must claim to be that account. Copy it from the generator's output, not from
  memory.
- **An invalid SteamID fails silently.** gbe_fork's example config says that if `account_steamid` is
  invalid, *"the emu will ignore it and generate a proper one"* — a random ID, which no longer matches
  the ticket. A typo looks exactly like a bad ticket.
- **Leave `alt_steamid` unset — unless the game's saves need it.** gbe_fork has an option that swaps
  the SteamID for another one after a number of calls (*"IT WILL REPLACE AFTER THOSE CALLS BE
  AWARE!"*). By default it only puts a different ID in front of Denuvo mid-run. Its real purpose is
  games whose **saves are encrypted with the SteamID**: there, players set it together with
  `alt_steamid_count`, and the right count is specific to each game and found by trial and error —
  reported on cs.rin.ru as 2 for DOOM and Stellar Blade, 3 for Monster Hunter Wilds, 4 for Resident
  Evil 4, 5 for Onimusha 2. Each wrong try can cost the activation and overwrite the save, so **back
  up your saves first**, and only reach for it if the game won't read its saves otherwise.
- **One ticket, one game.** It's generated for the AppID you typed. Each game needs its own.

### The limits

| Limit | What it means for you |
|---|---|
| **A ticket expires after 30 minutes** | Generate it, paste it, launch. A ticket from yesterday won't do — come back to the generator |
| **It can be reused within those 30 minutes** | Relaunching after a crash with the same ticket is fine. But it **does not save activations**: each launch that activates still counts |
| **5 activations per account per day** | The README's figure, counted per Steam account. Hit it and you wait for the next day — no setting changes that |

This sits on top of the [machine activation limit](#activation-limits) the publisher declares on the
store page, which is a separate, per-hardware count.

### What makes you lose the activation

Neither source documents how long an activation lasts once it's done, so no promise is made about
that here. What they do make clear is what sends you back to step 1 — and the players on cs.rin.ru's
Steam ticket thread add the hardware side from their own experience: the activation is tied to the
machine, so **an OS update, a hardware or BIOS change, or a driver update** can invalidate it; owning
only part of a game's **SecureDLC** while the setup claims more deletes it (a backup of it is no
help); and the `alt_steamid` trial and error above can too.

The hardware part matches how Denuvo is publicly described: the license saved by the game is built
from the machine it was requested on, and when the machine no longer matches, the game throws that
license away and asks for a new one — a new activation, and here a new ticket. In practice, expect
it after **a CPU change, adding or removing RAM, changing how many cores are enabled** (in the BIOS,
or the CPU count of a virtual machine) and **Windows updates**, feature updates above all. The
players' "driver update" isn't among the documented causes; treat it as reported, not established.

- **The ticket is older than 30 minutes** when the game asks for it.
- **The SteamID in `configs.user.ini` no longer matches** the account the ticket came from — edited,
  mistyped (and silently replaced, see above), or swapped mid-run by `alt_steamid`.
- **A new game, or a new AppID** — the ticket is per game.
- **A different machine or changed hardware** — that's the publisher's per-PC count from the store
  notice; a new activation needs a fresh ticket like any other.

When you do go back, each attempt can cost one of the five daily activations. If a launch fails,
check the SteamID before generating ticket after ticket.

---

## Why the rest of the repo doesn't apply

Each layer of this repo fails for its own reason, and it's worth knowing which, so you don't try to
combine them out of hope:

- **[Steamless](../running/Steamless%20Usage%20Guide.md)** only knows SteamStub. On a Denuvo binary it finds no
  `.bind` section and stops. Nothing to fix, nothing to force.
- **[Goldberg / RUNE](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md)** replace
  `steam_api64.dll`. On their own that isn't enough: Denuvo asks for an ownership ticket, and an
  emulator with nothing to give it fails the check. And the executable can't be patched to skip the
  check, because that code is virtualised and integrity-checked. **gbe_fork with a ticket from your
  own account is the exception** — [above](#running-a-denuvo-game-you-own-without-the-steam-client).
- **[eos-proxy](../multiplayer/EOS%20Proxy%20Usage%20Guide.md)** is a different layer entirely — it deals with a
  multiplayer login, not with whether the game will start.

Stacking all three on a Denuvo title, without the ticket, gets you exactly as far as installing none
of them.

---

## Hypervisor bypasses — what they cost

There now *is* something that gets a Denuvo game past its checks, and if you read any forum
you'll run into it, so it gets an entry here — as a price list, not a method. It doesn't remove
Denuvo and nothing in this repo will help you set it up.

**What it is.** A small kernel driver that installs itself as a bare-metal hypervisor, underneath
Windows, and answers Denuvo's hardware checks with whatever the cracked build expects. It works
because a hypervisor sees and controls everything the OS does — which is exactly what makes the
cost so high.

**What you have to switch off for it to load.** Windows will not run a third-party hypervisor
underneath its own, so its own has to go, along with everything built on it:

| Switched off | What it was doing for you |
|---|---|
| **Memory integrity (HVCI)** and the rest of virtualization-based security | Blocks tampering with the Windows kernel, even by code running as admin |
| **Credential Guard** | Keeps stored credentials out of reach of a compromised OS |
| **Driver signature enforcement** | Refuses kernel drivers Microsoft hasn't signed — the bypass driver is one of those |
| The Windows hypervisor itself (`hypervisorlaunchtype off`) | Hyper-V, **WSL 2** and **[Windows Sandbox](../index.md#verifying-what-you-download)** stop working until you turn it back on |

Windows Hello PIN or face login can break with it, and BitLocker can ask for its recovery key at the
next boot.

**What that means.** Each of those is a protection against the kind of malware that matters most
once it's in: one that wants the kernel. And the bypass itself runs at the highest privilege your
machine has, below the OS — a bug in that driver, or a doctored copy of it, would have complete and
undetectable access. Even the people who distribute these say so themselves, and their own
best-practice advice is telling: scan the machine first, take only releases whose tooling is open
source, keep the PC off the network while playing, have your BitLocker key and Windows password at
hand — and **revert every change and reboot as soon as you stop playing**.

**For an owner, the trade is rarely worth it.** Everything under
[What a legitimate owner can actually do](#what-a-legitimate-owner-can-actually-do) keeps your
machine's protections intact, and the [removal list](../lists/Denuvo.md) shows how often waiting
works. If you decide otherwise, do it on a machine or a VM with nothing personal on it — not on the
PC that holds your accounts.

---

## What a legitimate owner can actually do

### Check whether it's still there

**Denuvo is removed from a good number of games after release** — publishers drop it once the sales
window closes, usually in a plain patch. It's common enough that it should be your first check
rather than an afterthought: the store-page notice disappears, and both SteamDB and PCGamingWiki
record it.

If it was removed, everything in this repo applies again to the current build, and you have nothing
else to do.

How the people who maintain cs.rin.ru's list of uncracked Denuvo games settle it — no tool needed:

- **The store notice is a starting point, not proof.** It can be missing while the **EULA** carries
  the Denuvo clause (Heroes of Might and Magic III Remake and Rainbow Six Tactics were added that way
  in 2026) — the EULA link is at the bottom of the store page.
- **SteamDB's patch notes show it leaving.** When Denuvo goes, the main executable shrinks by a
  quarter of a gigabyte in one update: `Modified DOOMTheDarkAges.exe (-259.12 MiB)`,
  `Modified Retail/007FirstLight.exe (-263.21 MiB)`. A drop like that in the *Depots* history is the
  clearest sign there is.
- **It can go on one store and not another.** Two Point Campus lost it on the Epic build only; Total
  War: Pharaoh and Maneater came out DRM-free on GOG while the Steam version kept it. If you own the
  game twice, check both.
- **It can come back.** An update can add it to a game that shipped without it (Paranormasight: The
  Mermaid's Curse, February 2026) or put it back after a removal (The Climb). Re-check after updates
  rather than once.
- **"Denuvo Anti-Cheat" is a different product.** Some online games (Marauders, Tribes 3, eFootball,
  Fishing Planet, VAIL) carry Denuvo's anti-cheat rather than its anti-tamper; Steam reworded those
  store pages in April 2026. For those, the [anti-cheat list](../lists/Anti-Cheat.md) is the relevant
  one.

### Offline play

Denuvo titles generally allow offline play, within limits the publisher configures — typically after
a first online activation, and sometimes for a bounded period. That's the intended answer for "I want
to play without the client", and for many people it's enough. If it isn't,
[a ticket from your own account](#running-a-denuvo-game-you-own-without-the-steam-client) is the
next step.

### Activation limits

Activations are tied to your hardware, and a machine that changes too often can hit a limit. You
don't have to guess what it is: publishers declare it in the same store notice. The recurring
formulation is *"5 different PC within a day machine activation limit"* — five machines per 24 hours,
which only bites if you're reinstalling or swapping hardware often.

If you're hitting one, publisher support is the route, not tooling. The ticket method has a limit
of its own on top of this one — [five activations per account per day](#the-limits).

### A DRM-free edition

Some titles are sold DRM-free elsewhere, GOG in particular. If what you want is a copy that will
still run in ten years without asking anyone's permission, that's the version to own.

---

## For modding and reverse engineering

This is where it hurts most, because it's half of what this repo is for.

On a protected build, attaching a debugger is blocked by design. A disassembler still opens the
binary, but the functions you'd most want to read are precisely the ones Denuvo virtualises, so you
get its machinery instead of the game's. Injection-based tooling sometimes survives and sometimes
doesn't; it's title-by-title and not something to plan around.

The realistic paths, in order:

1. **Work on a build that doesn't have it.** If the DRM was removed in a patch, the current build is
   your target. [DepotDownloader](../game-files/DepotDownloader.md) gets you a specific build cleanly, and
   `-manifest-only` lets you inspect what's in one before downloading it.
2. **Work on a demo**, which is a separate app and usually ships without it. A free weekend is not
   the same thing — that's the full game's build, protection included.
3. **Work on the DRM-free edition** if one exists.

If none of those exist for your game, that's the answer: this one isn't available to you yet.
Waiting is a real strategy here — the removal patch arrives for a lot of titles.

---

## Links

- [SteamDB](https://steamdb.info/) — DRM notice and its history
- [PCGamingWiki](https://www.pcgamingwiki.com/) — DRM row, removal dates, offline-play notes
- [Steamless guide](../running/Steamless%20Usage%20Guide.md) — for the wrapper Denuvo is often confused with
- [steam-ticket-generator](https://github.com/denuvosanctuary/steam-ticket-generator) — EncryptedAppTicket
  from your own account, for gbe_fork's `ticket` field
