# Multiplayer — Which Tool, and With Whom

The tools in this repo don't compete on quality, they answer different questions. Which one applies
to your game is decided by **what its multiplayer runs on**, and you can usually tell before
installing anything.

Just as important, and usually skipped: each answer also decides **who you can play with**. Some put
you back on the real network with everyone else; some only connect you to other people running the
same setup.

---

## Work out the backend first

**First, does the game even have multiplayer?** Check the store page's category list — *Multi-player*,
*Online Co-op*, *Online PvP*. If none of them is there, stop: nothing to fix.

That check is not optional, because **shipping an SDK is not the same as using it**. Plenty of
single-player games carry `EOSSDK-Win64-Shipping.dll` for an engine plugin, cross-save or
achievements. Hades and Fading Echo both do, and neither has multiplayer at all.

Then look in the game folder, in this order:

| What you find | Backend | Go to |
|---|---|---|
| A `*_server.exe`, or a `Server/` folder | The game ships dedicated servers | [Dedicated servers](#dedicated-servers) |
| `EOSSDK-Win64-Shipping.dll` **and declared multiplayer** | Epic Online Services | [EOS](#eos) |
| `Photon*.dll`, `PlayFab*.dll`, coherence libraries | A third-party netcode service | [Secondary backends](#secondary-backends) |
| Only `steam_api64.dll` | Steam networking | [Steam networking](#steam-networking) |
| An EA / Ubisoft / Rockstar / Battle.net launcher | Publisher backend | [Nothing works](#publisher-backends) |

Unreal titles hide these under `<Game>\Binaries\Win64\` and `<Game>\Plugins\`, not the root folder.
A game can also have two — Steam lobbies for matchmaking and something else for the session — which
is why the tools below are stackable.

---

## Steam networking

The common case: lobbies, matchmaking and P2P through Steamworks. Two very different answers.

### gbe_fork — off Steam entirely

[Goldberg / gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) fakes the
whole Steam API, so the client doesn't even need to be running. What you get is **LAN discovery** —
so a virtual LAN (ZeroTier, Radmin) or `custom_broadcasts.txt` for direct addresses.

**Who you play with:** other people running the same emulator. Never a legitimate player.
**Account risk:** the lowest of everything here — you're not on Steam at all.

When it doesn't find the others — the checklist Mr_Goldberg kept repeating in his release thread,
still true of gbe_fork:

- **Windows calls the network *Private*** and the game is allowed through the firewall, on every PC.
- **Every player has a different SteamID.** Copying a whole game folder to a friend copies the ID with
  it: lobbies then show up, but joining fails. The global settings (name, language, ID) exist
  precisely so a game folder can be shared without them.
- **Everyone uses the same port** (`listen_port`, default 47584) — change it on one machine and that
  machine vanishes.
- **The virtual adapter is up before the game starts.** The emulator broadcasts on every network
  interface it finds at launch; a VPN that connects afterwards isn't on the list. Some VPNs (PPTP,
  TeamViewer VPN) don't carry broadcast at all — use `custom_broadcasts.txt` with the other players'
  addresses (DNS names work too), or ZeroTier/Radmin with broadcast enabled.
- **The experimental build blocks everything that isn't a private address** unless
  `disable_lan_only=1` (`configs.main.ini`) — Hamachi's `25.x.x.x` range included.
- To tell a firewall problem from an emulator problem, run two copies on **one** PC, each with its own
  `local_save_path`: if they see each other, the emulator is fine and the network isn't.

### uc-online2 — on the real Steam network

[uc-online2](uc-online2.md) is the opposite bet: it keeps the real client and makes the game report a
different AppID (Spacewar, `480`, the free app every account owns). Steam's real lobbies and
matchmaking then work.

**Who you play with:** other people running the same setup, on the same spoofed AppID.
**Account risk:** the highest here — a modified DLL on a live, logged-in Steam session.

---

## EOS

The game's netcode runs on Epic's servers even though you bought it on Steam.
[eos-proxy](EOS%20Proxy%20Usage%20Guide.md) swaps the login method and lets it connect.

**Who you play with:** **everyone.** This is the only case in the repo where you end up in the same
sessions as people who bought the game normally — the traffic really does go through Epic.
**Where it fails:** the developer can disable device-ID login, and then nothing client-side helps.
**Check every online feature, not just joining a match.** On Bodycam, eos-proxy got matches working
but not the in-game shop, which Online-Fix's package for the game did run — so even when EOS works,
compare it with the other routes before settling.

---

## Secondary backends

Photon, PlayFab, coherence and friends: the game uses Steam for identity and something else entirely
for the session. Neither gbe_fork nor eos-proxy touches these.

[uc-online2](uc-online2.md) carries plugins for exactly this — Photon, EOS, PlayFab, coherence — and
its installer detects which one a game uses. It's the only tool here that covers them.

---

## Dedicated servers

If the game ships server binaries, there is **nothing to emulate**. Run the server, connect by IP,
done. It's the least fashionable answer and often the best one: no DLL, no spoofing, no account
exposure, and it survives every game update.

Check for a separate "Dedicated Server" tool on Steam, a `Server/` folder in the install, or the
game's own documentation before reaching for anything else.

---

## Publisher backends

EA, Ubisoft Connect, Rockstar, Battle.net. The account check happens on their servers, with their
identity system. Nothing in this repo applies, and nothing else does either.

---

## The wall that no client-side tool passes

Worth understanding once, because it explains most of the failures you'll see reported.

When a game asks Steam for an **auth session ticket** and sends it to a server that validates it,
that server checks a signature produced with **Valve's private key**. A ticket that a client
fabricates is structurally correct and cryptographically worthless.

The consequence is a clean line:

- **Peer-to-peer checks** — both sides run the same tool, one mints a ticket, the other accepts it.
  This works.
- **Server-side validation** — the publisher's server asks Valve. This cannot work, ever, no matter
  which tool you use.

So a fix that "works for co-op" and fails on an official server isn't badly configured. It's on the
wrong side of that line.

### What it looks like in practice

**Subnautica 2**, 2026-08-10. Everything on the client side worked: the game launched with Steam
closed under gbe_fork, eos-proxy intercepted the Steam-ticket login and `EOS_Connect_Login` returned
`ResultCode: 0`. Three tools, all doing their job.

Then its own log:

```text
LogSonarAPI: Invalid response code 401 from https://api.live.subnautica.net/api/v1/player/friends/invite
LogSonarAPI: Sonar API access not granted (expired token?) - restarting session
LogOnlineFriend: Friends list refresh failed with error [Invalid response]
```

Friend codes come from **Sonar**, the studio's own service, which authenticates you before it hands
one out — and under an emulator the identity presented to it is fabricated (`SteamID 7656120…`,
persona `gse orca`). It answers 401 and keeps answering 401.

Nothing client-side changes that. Not gbe_fork, not eos-proxy, and not uc-online2 either: its ticket
emulation is peer-side by design, and a publisher's server asking Valve to validate is exactly the
case its own documentation says it cannot cover.

The lesson generalises: **a game can use Steam for identity, EOS for transport, and its own backend
for the feature you actually want.** Only the last one decides, and only the game's log names it.

---

## Summary

| Backend | Tool | With whom | Account risk |
|---|---|---|---|
| Steam, off-client | [gbe_fork](../running/Installation%20Guide%20-%20Goldberg%20Steam%20Emulator.md) | same-emulator players, LAN or VPN | lowest |
| Steam, real network | [uc-online2](uc-online2.md) | same-setup players | highest |
| EOS | [eos-proxy](EOS%20Proxy%20Usage%20Guide.md) | **everyone** | low |
| Photon / PlayFab / coherence | [uc-online2](uc-online2.md) plugins | same-setup players | highest |
| Dedicated servers | nothing needed | anyone you give the IP to | none |
| Publisher backends | — | — | — |
