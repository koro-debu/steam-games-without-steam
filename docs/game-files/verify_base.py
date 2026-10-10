#!/usr/bin/env python3
"""Check a game folder that didn't come from Steam against its depot manifest.

    python verify_base.py <depot>_<gid>.manifest [game folder] [--sample=N]

1. Is the manifest genuine? A depot chunk is addressed by its SHA-1, and Steam's
   content servers answer a HEAD on /depot/<depot>/chunk/<sha> with 200 if the
   chunk exists and 404 if it doesn't -- anonymously, without sending anything.
   A manifest whose sampled chunks all exist was built from Steam's data.
2. Are the files the ones it lists? Every file's size and SHA-1 is compared with
   the manifest. Files in the folder that the manifest doesn't know are listed
   separately: on a "clean" upload there should be none.

Standard library only. Reads files, sends HEAD requests to Steam, writes nothing.
"""
import hashlib
import io
import json
import os
import struct
import sys
import urllib.error
import urllib.request
import zipfile

SERVERS = ("https://api.steampowered.com/IContentServerDirectoryService/"
           "GetServersForSteamPipe/v1/?cell_id=0")
PAYLOAD, METADATA, END = 0x71F617D0, 0x1F4812BE, 0x32C415AB
FLAG_DIRECTORY = 64
FLAG_SYMLINK = 512  # no content of its own: points at another entry
NOT_A_FILE = FLAG_DIRECTORY | FLAG_SYMLINK


def varint(d, o):
    v = shift = 0
    while True:
        b = d[o]
        o += 1
        v |= (b & 0x7F) << shift
        if not b & 0x80:
            return v, o
        shift += 7


def fields(d):
    """(field, value) pairs of one protobuf message; nested messages stay bytes."""
    o = 0
    while o < len(d):
        tag, o = varint(d, o)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            v, o = varint(d, o)
        elif wire == 2:
            n, o = varint(d, o)
            v, o = d[o:o + n], o + n
        elif wire == 1:
            v, o = d[o:o + 8], o + 8
        elif wire == 5:
            v, o = d[o:o + 4], o + 4
        else:
            raise ValueError("unsupported wire type")
        yield field, v


def read_manifest(path):
    data = open(path, "rb").read()
    if data[:2] == b"PK":  # zipped: the single entry is the manifest
        z = zipfile.ZipFile(io.BytesIO(data))
        data = z.read(z.namelist()[0])
    sections, o = {}, 0
    while o + 8 <= len(data):
        magic, length = struct.unpack_from("<II", data, o)
        o += 8
        if magic == END:
            break
        sections[magic] = data[o:o + length]
        o += length
    meta = dict(fields(sections[METADATA]))
    files = []
    for field, mapping in fields(sections[PAYLOAD]):
        if field != 1:
            continue
        f = {"name": "", "size": 0, "flags": 0, "sha": b"", "chunks": []}
        for k, v in fields(mapping):
            if k == 1:
                f["name"] = v.decode("utf-8", "replace")
            elif k == 2:
                f["size"] = v
            elif k == 3:
                f["flags"] = v
            elif k == 5:
                f["sha"] = v
            elif k == 6:
                f["chunks"] += [c for ck, c in fields(v) if ck == 1]
        files.append(f)
    return meta.get(1), meta.get(2), bool(meta.get(4)), files


def head(host, depot, sha):
    url = f"https://{host}/depot/{depot}/chunk/{sha.hex()}"
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "verify_base"})
    try:
        return urllib.request.urlopen(req, timeout=10).status
    except urllib.error.HTTPError as e:
        return e.code
    except OSError:
        return None


def check_chunks(depot, files, sample):
    chunks = [f["chunks"][0] for f in files if f["chunks"]]
    if not chunks:
        print("chunks   : the manifest lists no chunks, nothing to check")
        return None
    picked = sorted({chunks[i * len(chunks) // sample] for i in range(min(sample, len(chunks)))})
    try:
        servers = json.load(urllib.request.urlopen(SERVERS, timeout=15))["response"]["servers"]
    except (OSError, ValueError, KeyError):
        print("chunks   : Steam's server list is unreachable, check skipped")
        return None
    hosts = [s["host"] for s in sorted(servers, key=lambda s: s.get("weighted_load", 100))
             if s.get("type") in ("SteamCache", "CDN") and s.get("https_support") != "unavailable"]
    present = missing = unknown = 0
    for sha in picked:
        status = head(hosts[0], depot, sha)
        if status == 404 and len(hosts) > 1:  # one cache's 404 could be its own fault
            status = head(hosts[1], depot, sha)
        if status == 200:
            present += 1
        elif status == 404:
            missing += 1
            print(f"           missing on Steam: {sha.hex()}")
        else:
            unknown += 1
    print(f"chunks   : {present} present, {missing} missing, {unknown} no answer "
          f"(sampled {len(picked)} of {len(chunks)} files, via {hosts[0]})")
    return missing == 0 and present > 0


def check_folder(folder, files, encrypted):
    if encrypted:
        print("files    : this manifest's file names are still encrypted -- use the one from "
              "Steam's depotcache, which stores them in the clear")
        return None
    listed, bad, gone = set(), 0, 0
    for f in files:
        rel = f["name"].replace("\\", os.sep)
        listed.add(os.path.normcase(os.path.normpath(rel)))
        if f["flags"] & NOT_A_FILE:
            continue
        path = os.path.join(folder, rel)
        if not os.path.isfile(path):
            gone += 1
            print(f"           missing: {f['name']}")
            continue
        h = hashlib.sha1()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        if os.path.getsize(path) != f["size"] or (f["sha"] and h.digest() != f["sha"]):
            bad += 1
            print(f"           DIFFERENT: {f['name']}")
    extra = []
    for root, _, names in os.walk(folder):
        for n in names:
            rel = os.path.normcase(os.path.normpath(os.path.relpath(os.path.join(root, n), folder)))
            if rel not in listed:
                extra.append(rel)
    for rel in sorted(extra):
        print(f"           not in the manifest: {rel}")
    count = sum(1 for f in files if not f["flags"] & NOT_A_FILE)
    print(f"files    : {count - bad - gone} match, {bad} different, {gone} missing, "
          f"{len(extra)} not in the manifest")
    return bad == 0 and gone == 0 and not extra


def main(argv):
    args = [a for a in argv if not a.startswith("--sample")]
    sample = next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--sample=")), 16)
    if not args:
        print(__doc__)
        return 2
    depot, gid, encrypted, files = read_manifest(args[0])
    print(f"manifest : depot {depot}, gid {gid}, {len(files)} entries")
    verdicts = [check_chunks(depot, files, sample)]
    if len(args) > 1:
        verdicts.append(check_folder(args[1], files, encrypted))
    if False in verdicts:
        print("RESULT   : does NOT match -- see above")
        return 1
    if None in verdicts:
        print("RESULT   : no mismatch found, but not everything could be checked")
        return 0
    print("RESULT   : matches")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
