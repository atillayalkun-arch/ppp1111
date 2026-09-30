#!/usr/bin/env python3
"""Asama A: YouTube Data API'den kanal ve videolarin HAM verisini eksiksiz toplar.

Hicbir eleme/secim yapmaz; tum kanal gecmisini (Shorts dahil) kaydeder.
Analiz ve secim sonraki asamalardadir (analyze.py, select_sample.py), boylece
kurallari degistirmek icin API'yi tekrar cagirmak gerekmez.

Girdi : channels.txt   satir bicimi:  <link | @handle | UC...> | <sinif> | <not>
        sinif: core / neighbor / global / own     not: serbest (ornegin arama kelimesi)
Cikti : data/raw/<channel_id>.json  (API'nin verdigi tum alanlar)

    export YT_API_KEY=...            (PowerShell: $env:YT_API_KEY="...")
    python collect.py channels.txt [--refresh]
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3"
RAW = Path("data/raw")

CHANNEL_PARTS = "snippet,statistics,contentDetails,brandingSettings,topicDetails,status"
VIDEO_PARTS = ("snippet,contentDetails,statistics,status,topicDetails,"
               "liveStreamingDetails,recordingDetails,paidProductPlacementDetails")
VIDEO_PARTS_SAFE = "snippet,contentDetails,statistics,status,topicDetails,liveStreamingDetails"


def api(endpoint, **params):
    params["key"] = os.environ["YT_API_KEY"]
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            if e.code == 403 and "quota" in body.lower():
                sys.exit("HATA: gunluk API kotasi doldu. Yarin ayni komutu calistir; bitenler atlanir.")
            if e.code in (500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{endpoint} HTTP {e.code}: {body[:300]}")
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def resolve_channel(ref):
    """link / @handle / UC id -> channels.list ogesi."""
    ref = urllib.parse.unquote(ref.strip())
    m = re.search(r"(UC[\w-]{22})", ref)
    if m:
        res = api("channels", part=CHANNEL_PARTS, id=m.group(1))
    else:
        m = re.search(r"(@[^/?#\s]+)", ref)
        if m:
            res = api("channels", part=CHANNEL_PARTS, forHandle=m.group(1))
        else:
            m = re.search(r"youtube\.com/(?:c|user)/([^/?#\s]+)", ref)
            name = m.group(1) if m else ref
            res = api("channels", part=CHANNEL_PARTS, forUsername=name)
            if not res.get("items"):  # son care: arama (100 kota birimi)
                s = api("search", part="snippet", q=name, type="channel", maxResults=1)
                if s.get("items"):
                    res = api("channels", part=CHANNEL_PARTS, id=s["items"][0]["snippet"]["channelId"])
    if not res.get("items"):
        raise RuntimeError("kanal bulunamadi")
    return res["items"][0]


def paged(endpoint, max_pages=200, **params):
    page = None
    for _ in range(max_pages):
        res = api(endpoint, **({**params, "pageToken": page} if page else params))
        yield from res.get("items", [])
        page = res.get("nextPageToken")
        if not page:
            return


def fetch_videos(uploads_id):
    ids = [it["contentDetails"]["videoId"]
           for it in paged("playlistItems", part="contentDetails", playlistId=uploads_id, maxResults=50)]
    parts, videos = VIDEO_PARTS, []
    for i in range(0, len(ids), 50):
        batch = ",".join(ids[i:i + 50])
        try:
            res = api("videos", part=parts, id=batch)
        except RuntimeError as e:
            if "HTTP 400" not in str(e) or parts == VIDEO_PARTS_SAFE:
                raise
            parts = VIDEO_PARTS_SAFE  # desteklenmeyen bir part varsa guvenli listeye don
            res = api("videos", part=parts, id=batch)
        videos.extend(res.get("items", []))
    return videos


def parse_line(line):
    p = [x.strip() for x in line.split("|")]
    return p[0], (p[1].lower() if len(p) > 1 else ""), (p[2] if len(p) > 2 else "")


def main():
    if "YT_API_KEY" not in os.environ:
        sys.exit("HATA: YT_API_KEY ortam degiskeni yok.")
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    refresh = "--refresh" in sys.argv
    src = Path(args[0] if args else "channels.txt")
    lines = [l for l in src.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.lstrip().startswith("#")]
    RAW.mkdir(parents=True, exist_ok=True)

    seen, failed = set(), []
    for n, line in enumerate(lines, 1):
        ref, cls, note = parse_line(line)
        try:
            ch = resolve_channel(ref)
            cid = ch["id"]
            if cid in seen:
                print(f"[{n}/{len(lines)}] ATLANDI (tekrar): {ch['snippet']['title']}")
                continue
            seen.add(cid)
            path = RAW / f"{cid}.json"
            if path.exists() and not refresh:
                print(f"[{n}/{len(lines)}] var, atlandi: {ch['snippet']['title']}")
                continue
            videos = fetch_videos(ch["contentDetails"]["relatedPlaylists"]["uploads"])
            playlists = list(paged("playlists", max_pages=5, part="snippet,contentDetails",
                                   channelId=cid, maxResults=50))
            path.write_text(json.dumps({
                "meta": {"ref": ref, "class": cls, "note": note,
                         "collected_at": datetime.now(timezone.utc).isoformat()},
                "channel": ch, "playlists": playlists, "videos": videos,
            }, ensure_ascii=False), encoding="utf-8")
            print(f"[{n}/{len(lines)}] {ch['snippet']['title']}: {len(videos)} video, {len(playlists)} oynatma listesi")
        except Exception as e:  # tek kanal hatasi tumunu durdurmasin
            print(f"[{n}/{len(lines)}] HATA {ref}: {e}")
            failed.append(ref)
    print(f"\nBitti. Ham veri: {RAW}/")
    if failed:
        print("Cozumlenemeyen kanallar:", *failed, sep="\n  ")


if __name__ == "__main__":
    main()
