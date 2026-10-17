# EOS Proxy — Usage Guide

`eos-proxy` is a **DLL proxy for the Epic Online Services SDK**. It sits in front of
`EOSSDK-Win64-Shipping.dll` and swaps the EOS login from *Steam session ticket* to *device ID
access token*, so a game's EOS multiplayer comes up without a valid Steam auth ticket.

It is not an emulator: **all multiplayer traffic still goes through Epic's own servers**. It only
changes how the game logs in to them.

> **For legal owners only.** This is about playing a game you bought with friends who also bought
> it, when the Steam authentication path is unavailable (offline account, Goldberg, family
> account). It does not bypass a purchase, it does not touch [Denuvo](../other/Denuvo.md), and it grants no access to
> anything Epic doesn't already hand out for free.
> Circumventing authentication can be unlawful even for personal use in some jurisdictions
> (DMCA in the US, EUCD in the EU) — check before you start.

---

## Do you actually need it?

This is the third of the three layers described in the [README](../index.md) — the one that only
matters once the game already runs. If you're not sure your game's multiplayer is EOS at all, start
from [Which tool, and with whom](Multiplayer%20Routing.md).

| Reach for it when… | Skip it when… |
|---|---|
| `EOSSDK-Win64-Shipping.dll` is there **and the game has multiplayer** | The store lists no multiplayer — the SDK ships with plenty of single-player games |
| Singleplayer works but multiplayer never connects | The game's multiplayer is pure Steam (Goldberg + LAN is enough) |
| The lobby/friends UI hangs on "signing in" | The game uses Easy Anti-Cheat online (see [Limits](#limits)) |

Goldberg's LAN emulation and this are **different problems**. Goldberg fakes the Steam API;
eos-proxy fixes the Epic login. A game that uses EOS for its netcode needs the EOS layer even
with Goldberg working perfectly.

---

## Download

Upstream repository: <https://github.com/yesyes0649/eos-proxy>

| Branch / release | What it is |
|---|---|
| `main` — release **v1.0.0** | Prebuilt `EOSSDK-Win64-Shipping.dll`, the login swap only |
| `dev` — commit `8c5c959` | Same, **plus** `EOS_Platform_Create` forces `IntegratedPlatformOptionsContainerHandle` to `NULL` (drops the Steam integrated-platform bridge that makes some games fail early). No release build — compile it yourself |
| `absolum` — release **absolum** | Game-specific variant for *Absolum* |

No license file, no code signature. Everything is a handful of C files; read them before running
the binary, or build from source — it takes about ten seconds (see below).

> Antivirus will flag it: a DLL that shadows another DLL and forwards 671 exports is textbook
> hijack behaviour. Expected for this category of tool.

**What the v1.0.0 binary actually is** (checked 2026-08-09, sha256 `00e0f034…0d23916`, pinned in
here): 672 exports, of which 671 forward to `EOSSDK-Win64-Shipping.yes` under
identical names and one — `EOS_Connect_Login` — is implemented in the proxy. That matches the
published source exactly. It imports nothing from the network, registry or process-creation APIs;
the only file it writes is its log. VirusTotal 3/70, all three machine-learning heuristics
(including Microsoft's `Wacatac.B!ml`, the classic false positive on unsigned low-prevalence
binaries), sandbox verdict clean. `EOS_Platform_Create` is absent from it — that one only exists on
`dev`, which confirms which branch the release was built from.

---

## Install

Two steps, then launch:

1. In the game's folder, **rename `EOSSDK-Win64-Shipping.dll` to `EOSSDK-Win64-Shipping.yes`**
   (it sits next to the executable — e.g. `…\<Game>\Binaries\Win64\`). Don't move it and don't
   delete it: the proxy loads it by that exact name and forwards everything else to it.
2. **Drop the proxy `EOSSDK-Win64-Shipping.dll`** in that same folder.

Launch the game. A fresh `epic_proxy.log` next to the executable means the proxy is live.

That's the whole EOS side — no configuration, nothing to fill in. It sits **on top of whatever already
makes the game start without Steam**, which in practice is [gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md):
the reason to reach for eos-proxy is playing outside Steam, and without a Steam layer the game doesn't
launch at all. gbe_fork isn't something eos-proxy needs configured for it — the two simply go together.
**Bodycam** and **Big Walk** were set up exactly like this on 2026-10-10: game already running under
gbe_fork, then the two steps above, nothing else. On Bodycam that got online play working, **but not
the in-game shop** — see [Confirmed games](#confirmed-games).

To uninstall: delete the proxy DLL and rename `.yes` back to `.dll`.

---

## The Steam side goes with it

Most games call `ISteamUser::GetAuthTicketForWebApi` **before** touching EOS and give up if it
errors out, and the proxy does nothing about that — the Steam layer answers it. Use whichever one
already runs your game:

| Tool | When to use it | Notes |
|---|---|---|
| [gbe_fork](https://github.com/Detanup01/gbe_fork/) | You want the game fully independent of Steam | Already covered in the [Goldberg guide](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md). Steam invites won't interoperate with the two below |
| [uc-online2](uc-online2.md) | Real Steam client running, Online-Fix-like experience | Closest thing to "it just works". Take it from the **active fork**, `LukeWarmSodas/uc-online2`, not the `UnionCrax-Team` repo linked in upstream's docs |
| [SLSsteam](https://github.com/AceSLS/SLSsteam/) | **Linux only** | Needs `FakeAppIds` configured for the game |

Everyone in the lobby should be on the same side of that fence: gbe_fork users and
uc-online2/SLSsteam users can't send each other Steam invites. Joining through Epic still works.

---

## How it works

Worth knowing, because it explains every failure mode:

1. **DllMain** loads `EOSSDK-Win64-Shipping.yes` and opens `epic_proxy.log`. All 671 other exports are
   forwarded straight through with linker `/export:…=EOSSDK-Win64-Shipping.yes.…` directives. The
   proxy implements only what it actually changes: `EOS_Connect_Login`, plus `EOS_Platform_Create`
   on `dev` — which is why the v1.0.0 binary has exactly 671 forwards and one own function.
2. **`EOS_Connect_Login`** is intercepted. Instead of passing the game's credentials
   (`Type = EOS_ECT_STEAM_SESSION_TICKET`), it first calls `EOS_Connect_CreateDeviceId`, using
   your **SteamID as `DeviceModel`** so the device ID is stable and unique per player.
3. In that callback it retries the login with `Type = 10`
   (`EOS_ECT_DEVICEID_ACCESS_TOKEN`), `Token = NULL`, and your **Steam persona name** as
   `DisplayName`. Then the game's original callback is invoked as if nothing happened.
   `ResultCode 24` from `CreateDeviceId` ("already exists") is treated as success.
4. **`EOS_Platform_Create`** (dev branch) nulls out `IntegratedPlatformOptionsContainerHandle`,
   which disables the EOS ↔ Steam integrated-platform bridge some games configure.

Consequences: your EOS identity is a **brand-new anonymous device account**, not an Epic account —
no persistent friends list, no cross-progression, and the display name comes from Steam. If the
developer disabled Device ID login in their EOS product config, none of this works and there is
no workaround on the client side.

---

## Building from source

Needed for the `dev` branch, and the sane option in general.

Requirements: **Visual Studio Build Tools** with the C++ workload (MSVC + Windows SDK). Open
*x64 Native Tools Command Prompt for VS* — the x86 prompt produces a 32-bit DLL that won't load.

```bat
git clone -b dev https://github.com/yesyes0649/eos-proxy
cd eos-proxy
build.bat
```

`build.bat` is a one-liner:

```bat
cl /W3 /we4013 /LD /O2 /EHsc ../src/main.c /link /DLL /OUT:EOSSDK-Win64-Shipping.dll User32.lib
```

Output lands in `build\EOSSDK-Win64-Shipping.dll`. Copy it into the game folder as described
above. There is no dependency on the EOS SDK headers — the handful of structs it needs are
redeclared in `src/main.c`.

---

## Troubleshooting

Everything goes to **`epic_proxy.log`**, next to the game executable. Login errors also raise a
message box and then kill the process, so a silent crash *after* startup is generally not the proxy.

The exception is load time: if it can't open `EOSSDK-Win64-Shipping.yes`, `DllMain` just fails, with
nothing but a line in the log and whatever error Windows decides to show. Check the log first.

| Symptom | Cause | Fix |
|---|---|---|
| No `epic_proxy.log` at all | Proxy never loaded | Wrong folder, or 32-bit build, or the game loads the SDK from elsewhere |
| Log says `FATAL: could not load EOSSDK-Win64-Shipping.yes` | The original DLL wasn't renamed, or was deleted | Restore it under the exact `.yes` name |
| `ERROR when calling EOS_Connect_Login` box | Epic refused the device-ID login | Usually the developer disabled that login type — dead end |
| `ERROR when calling EOS_Connect_CreateDeviceId` box | Same, at the device-creation step | Check the `ResultCode` in the log against Epic's `EOS_EResult` list |
| Log shows a SteamID of `0` / empty persona name | The Steam layer isn't answering | Fix the gbe_fork / uc-online2 / SLSsteam setup first |
| Game starts, multiplayer still dead | The game never called EOS | Missing `GetAuthTicketForWebApi` response — same fix as above |

---

## Confirmed games

Upstream has tested very few. Treat anything else as unknown.

| Game | Status |
|---|---|
| Sledding Game | Works |
| Bodycam | **Partly.** Online play works with gbe_fork + the two install steps (tested here, 2026-10-10); the **in-game shop doesn't**. Online-Fix's package for the same game had the shop working too (tested here; that package was not audited) |
| Big Walk | Same (tested here, 2026-10-10) |
| SpiderHeck | Works, but **not** with gbe_fork — use uc-online2 or SLSsteam |
| Absolum | Needs the `absolum` branch |

---

## A login that works is not multiplayer that works

Worth knowing before you read the log as a verdict. On **Subnautica 2** (2026-08-10) the proxy did
everything it is supposed to:

```text
[PROXY] Loaded EOSSDK-Win64-Shipping.yes at 0x00007FFEC0090000
EOS_Connect_Login | Type: 18          <- the game asked for a Steam session ticket
CALLBACK --- EOS_Connect_CreateDeviceId   ResultCode: 0
CALLBACK --- EOS_Connect_Login            ResultCode: 0
```

`Type: 18` is `EOS_ECT_STEAM_SESSION_TICKET` — exactly the case this proxy exists for — and both
callbacks returned 0. The EOS connection is up. **And the game still could not generate a friend
code.**

So a clean log proves one thing only: the *login* succeeded. Whatever the game builds on top —
lobbies, friend codes, its own backend — is a separate mechanism, and a shipped EOS SDK does not mean
every online feature runs through it. Under gbe_fork the game also has a fabricated Steam identity
(`SteamID Fetched: 7656120…`, persona `gse orca`), which anything tied to a real Steam account has
nothing to attach to.

The game's own log named the culprit. Its friend codes come from **Sonar**, Unknown Worlds' backend:

```text
LogSonarAPI: Invalid response code 401 from https://api.live.subnautica.net/api/v1/player/friends/invite
LogSonarAPI: Attempting to create an http request without being logged in
LogOnlineFriend: Friends list refresh failed with error [Invalid response]
```

**401 Unauthorized**, from their server, to an identity that isn't real. EOS was never the gate. No
client-side tool reaches that — see [the wall](Multiplayer%20Routing.md#the-wall-that-no-client-side-tool-passes).

Read the log to tell these apart:

| What the log shows | What it means |
|---|---|
| No log at all | The proxy never loaded — wrong SDK replaced, or the game reads it elsewhere |
| `ERROR when calling EOS_Connect_Login` | Epic refused the device-ID login. Developer-side, nothing to do |
| `ResultCode: 0` and multiplayer still dead | The sessions do not run on EOS, or need more than a login — check the game's own log next |
| Matches work, but the shop / unlocks / leaderboards don't | Those features sit on another backend than the sessions (Bodycam). Test each online feature, not just joining a game |

---

## Limits

- **Developer-side kill switch.** Device ID login can be disabled per product in the EOS
  developer portal. When it is, the proxy fails at login and there's nothing to be done.
- **Anti-cheat.** Games using EasyAntiCheat online will refuse this; the proxy forwards the
  `EOS_AntiCheat*` exports untouched but doesn't try to defeat anything. Don't take it into a
  competitive lobby.
- **No Epic account.** Anonymous device account only — no friends, no cross-platform progression,
  and the account is tied to the machine (and to the SteamID used as `DeviceModel`).
- **Not a Steam emulator.** It only fixes the EOS login; the game still needs its Steam layer —
  normally gbe_fork (see [above](#the-steam-side-goes-with-it)).
- **x64 only**, Windows binary. Upstream's own instructions cover a Linux-only companion tool
  (SLSsteam), so it is clearly used under Proton — but that's inference from their docs, not
  something tested here.

---

## And fully offline?

eos-proxy keeps you on Epic's servers. If what you want is an EOS game with no network at all, the
situation in 2026 (cs.rin.ru's three EOS-emulator threads, read in full):

1. **Try without an EOS emulator first.** Plenty of Steam games use EOS only for online features:
   with gbe_fork on the Steam side and Epic's original `EOSSDK-Win64-Shipping.dll` left alone, the
   single-player part runs. Many Steam games log into EOS *with a Steam ticket*; gbe_fork's defaults
   (`new_app_ticket=1`, `gc_token=1` in `configs.main.ini`) produce the modern ticket that expects —
   the original Goldberg's tickets get rejected.
2. **If the game insists on EOS**, the only emulator that works with current EOS SDKs is
   **Nemirtingas Epic Emulator** — offline auth, DLC, achievements, LAN. It has been **closed source
   since 2022**, its recent builds circulate as forum attachments (1.6.4, April 2026, posted by staff
   on a locked thread), and newer network builds went to donors only. Not auditable; the
   [closed-source page](../other/Closed-Source%20Tools.md) applies in full.
3. The open ones are dead: **nEOS** (source on GitLab, frozen at EOS SDK 1.3, 2019) and **Goldberg's
   EOS emulator** (closed, v0.0.2, 2019).

None of them lets you play with legitimate Epic players — that's what eos-proxy is for.

---

## Upstream projects

| Tool | Repository |
|---|---|
| eos-proxy | <https://github.com/yesyes0649/eos-proxy> |
| gbe_fork | <https://github.com/Detanup01/gbe_fork> |
| uc-online2 (active fork) | <https://github.com/LukeWarmSodas/uc-online2> |
| SLSsteam (Linux) | <https://github.com/AceSLS/SLSsteam> |
| EOS SDK reference (`EOS_EResult`, login types) | <https://dev.epicgames.com/docs/api-ref> |
