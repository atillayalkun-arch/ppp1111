#!/usr/bin/env python3
"""Faz 0, adim 2-4: kanal profili + video listesi + orneklem secimi.

Girdi : channels.txt  (her satir: <kanal linki | @handle | UC...>  [| grup])
Cikti : out/channels.csv, out/videos.csv, out/sample.csv, out/channel_briefs.json

Sadece standart kutuphane kullanir. YouTube Data API v3 anahtari gerekir:
    export YT_API_KEY=...        (Windows PowerShell: $env:YT_API_KEY="...")
    python collect_channels.py channels.txt
"""
import csv
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3"
WINDOW_DAYS = 365        # son kac gunun videolari
MIN_LONG_SEC = 240       # bunun altindaki videolar "kisa" sayilir (Shorts dahil)
MATURE_DAYS = 14         # bundan yeni videolar outlier hesabina girmez
STALLED_DAYS = 60        # son yuklemeden beri bu kadar gun gectiyse "durmus"
MIN_LONG_FOR_SAMPLE = 8  # bundan az uzun video varsa kanal "few_long_videos"
N_TOP, N_MID, N_LOW = 3, 2, 2

OUT = Path("out")
CACHE = OUT / "cache"


# ---------------------------------------------------------------- API ----
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
                sys.exit("HATA: gunluk API kotasi doldu. Yarin ayni komutu tekrar calistir (cache sayesinde kalinan yerden devam eder).")
            if e.code in (500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"{endpoint} HTTP {e.code}: {body[:300]}")
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def parse_duration(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ------------------------------------------------------- kanal cozumleme ----
def parse_line(line):
    parts = [p.strip() for p in line.split("|")]
    return parts[0], (parts[1] if len(parts) > 1 else "")


def resolve_channel(ref):
    """link / @handle / UC id -> channels.list sonucu (snippet,statistics,contentDetails)."""
    ref = urllib.parse.unquote(ref.strip())
    part = "snippet,statistics,contentDetails"
    m = re.search(r"(UC[\w-]{22})", ref)
    if m:
        res = api("channels", part=part, id=m.group(1))
    else:
        m = re.search(r"(@[^/?#\s]+)", ref)
        if m:
            res = api("channels", part=part, forHandle=m.group(1))
        else:
            m = re.search(r"youtube\.com/(?:c|user)/([^/?#\s]+)", ref)
            name = m.group(1) if m else ref
            res = api("channels", part=part, forUsername=name)
            if not res.get("items"):  # son care: arama (100 kota birimi)
                s = api("search", part="snippet", q=name, type="channel", maxResults=1)
                if s.get("items"):
                    res = api("channels", part=part, id=s["items"][0]["snippet"]["channelId"])
    items = res.get("items") or []
    if not items:
        raise RuntimeError("kanal bulunamadi")
    return items[0]


# ---------------------------------------------------------- video toplama ----
def fetch_videos(uploads_id, cutoff):
    ids, page = [], None
    while True:
        params = dict(part="contentDetails", playlistId=uploads_id, maxResults=50)
        if page:
            params["pageToken"] = page
        res = api("playlistItems", **params)
        stop = False
        for it in res.get("items", []):
            pub = it["contentDetails"].get("videoPublishedAt")
            if pub and parse_ts(pub) < cutoff:
                stop = True
                continue
            ids.append(it["contentDetails"]["videoId"])
        page = res.get("nextPageToken")
        if stop or not page:
            break
    videos = []
    for i in range(0, len(ids), 50):
        res = api("videos", part="snippet,contentDetails,statistics", id=",".join(ids[i:i + 50]))
        videos.extend(res.get("items", []))
    return videos


def video_row(v, now):
    st, sn = v.get("statistics", {}), v["snippet"]
    pub = parse_ts(sn["publishedAt"])
    age_h = max((now - pub).total_seconds() / 3600, 1)
    views = int(st.get("viewCount", 0))
    likes = int(st.get("likeCount", 0))
    comments = int(st.get("commentCount", 0))
    dur = parse_duration(v["contentDetails"].get("duration"))
    return {
        "video_id": v["id"],
        "url": f"https://www.youtube.com/watch?v={v['id']}",
        "title": sn["title"],
        "published": pub.date().isoformat(),
        "age_days": round(age_h / 24, 1),
        "duration_min": round(dur / 60, 1),
        "is_long": dur >= MIN_LONG_SEC,
        "views": views,
        "likes": likes,
        "comments": comments,
        "like_rate": round(likes / views, 4) if views else 0,
        "engagement": round((likes + comments) / views, 4) if views else 0,
        "vph_avg": round(views / age_h, 1),
        "thumbnail": (sn.get("thumbnails", {}).get("maxres")
                      or sn.get("thumbnails", {}).get("high") or {}).get("url", ""),
    }


# ------------------------------------------------------- analiz / secim ----
def add_outliers(rows):
    """Olgun uzun videolarin medyanina gore outlier orani. Cok yeni videolar isaretlenir."""
    base = [r["views"] for r in rows if r["is_long"] and r["age_days"] >= MATURE_DAYS]
    med = statistics.median(base) if base else 0
    for r in rows:
        r["too_new"] = r["age_days"] < MATURE_DAYS
        r["outlier_ratio"] = round(r["views"] / med, 2) if med and r["is_long"] and not r["too_new"] else ""
    return med


def select_sample(rows):
    """Olgun uzun videolardan: en iyi N_TOP, medyana en yakin N_MID, en kotu N_LOW."""
    pool = [r for r in rows if r["is_long"] and not r["too_new"] and r["outlier_ratio"] != ""]
    if not pool:
        return []
    if len(pool) <= N_TOP + N_MID + N_LOW:
        for r in pool:
            r["sample_role"] = "all"
        return pool
    by_ratio = sorted(pool, key=lambda r: r["outlier_ratio"], reverse=True)
    top = by_ratio[:N_TOP]
    low = by_ratio[-N_LOW:]
    rest = [r for r in by_ratio if r not in top and r not in low]
    mid = sorted(rest, key=lambda r: abs(r["outlier_ratio"] - 1))[:N_MID]
    for role, group in (("top", top), ("mid", mid), ("low", low)):
        for r in group:
            r["sample_role"] = role
    return top + mid + low


def channel_row(ch, group, rows, median_views, now):
    sn, st = ch["snippet"], ch["statistics"]
    created = parse_ts(sn["publishedAt"])
    longs = [r for r in rows if r["is_long"]]
    shorts = len(rows) - len(longs)
    subs = int(st.get("subscriberCount", 0))
    span_days = max(min((now - created).days, WINDOW_DAYS), 1)
    last_upload = min((r["age_days"] for r in rows), default=None)
    mature_ratios = [r["outlier_ratio"] for r in longs if r["outlier_ratio"] != ""]
    flags = []
    if st.get("hiddenSubscriberCount"):
        flags.append("hidden_subs")
    if last_upload is None or last_upload > STALLED_DAYS:
        flags.append("stalled")
    if len(longs) < MIN_LONG_FOR_SAMPLE:
        flags.append("few_long_videos")
    if (now - created).days < 365:
        flags.append("new_channel")
    return {
        "group": group,
        "channel": sn["title"],
        "handle": sn.get("customUrl", ""),
        "url": f"https://www.youtube.com/channel/{ch['id']}",
        "channel_id": ch["id"],
        "country": sn.get("country", ""),
        "created": created.date().isoformat(),
        "channel_age_days": (now - created).days,
        "subs": subs,
        "total_videos": int(st.get("videoCount", 0)),
        "total_views": int(st.get("viewCount", 0)),
        "long_videos_12m": len(longs),
        "shorts_12m": shorts,
        "uploads_per_week_long": round(len(longs) / (span_days / 7), 2),
        "median_duration_min": round(statistics.median([r["duration_min"] for r in longs]), 1) if longs else "",
        "median_views_long": int(median_views),
        "median_views_per_sub": round(median_views / subs, 3) if subs else "",
        "max_outlier_ratio": max(mature_ratios, default=""),
        "share_outliers_2x": round(sum(x >= 2 for x in mature_ratios) / len(mature_ratios), 2) if mature_ratios else "",
        "days_since_last_upload": last_upload if last_upload is not None else "",
        "flags": ",".join(flags),
        "description": " ".join(sn.get("description", "").split())[:300],
    }


def brief(chrow, rows):
    """Bir AI modeline verilecek kompakt ozet (token dostu)."""
    longs = sorted((r for r in rows if r["is_long"]), key=lambda r: r["views"], reverse=True)
    pick = lambda rs: [{"title": r["title"], "views": r["views"], "min": r["duration_min"],
                        "age_days": r["age_days"], "outlier": r["outlier_ratio"]} for r in rs]
    return {k: chrow[k] for k in ("group", "channel", "handle", "created", "subs", "flags",
                                  "uploads_per_week_long", "median_duration_min",
                                  "median_views_long", "max_outlier_ratio", "description")} | {
        "top_titles": pick(longs[:10]),
        "bottom_titles": pick(longs[-5:] if len(longs) > 10 else []),
    }


# ------------------------------------------------------------------ ana ----
def process(ref, group, now, cutoff):
    key = re.sub(r"\W+", "_", urllib.parse.unquote(ref))[:80]
    cache = CACHE / f"{key}.json"
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        return data["ch"], data["videos"]
    ch = resolve_channel(ref)
    videos = fetch_videos(ch["contentDetails"]["relatedPlaylists"]["uploads"], cutoff)
    cache.write_text(json.dumps({"ch": ch, "videos": videos}, ensure_ascii=False), encoding="utf-8")
    return ch, videos


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    if "YT_API_KEY" not in os.environ:
        sys.exit("HATA: YT_API_KEY ortam degiskeni yok.")
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "channels.txt")
    lines = [l for l in src.read_text(encoding="utf-8").splitlines() if l.strip() and not l.lstrip().startswith("#")]
    OUT.mkdir(exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=WINDOW_DAYS)

    channels, all_videos, sample, briefs, failed = [], [], [], [], []
    for n, line in enumerate(lines, 1):
        ref, group = parse_line(line)
        try:
            ch, videos = process(ref, group, now, cutoff)
        except Exception as e:  # tek kanal hatasi tumunu durdurmasin
            print(f"[{n}/{len(lines)}] HATA {ref}: {e}")
            failed.append(ref)
            continue
        rows = [video_row(v, now) for v in videos]
        med = add_outliers(rows)
        chrow = channel_row(ch, group, rows, med, now)
        picked = select_sample(rows)
        for r in rows:
            r.update(channel=chrow["channel"], group=group, sample_role=r.get("sample_role", ""))
        channels.append(chrow)
        all_videos.extend(rows)
        sample.extend(picked)
        briefs.append(brief(chrow, rows))
        print(f"[{n}/{len(lines)}] {chrow['channel']}: {len(rows)} video, orneklem {len(picked)}, flags={chrow['flags'] or '-'}")

    write_csv(OUT / "channels.csv", channels)
    write_csv(OUT / "videos.csv", all_videos)
    write_csv(OUT / "sample.csv", sample)
    (OUT / "channel_briefs.json").write_text(json.dumps(briefs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nBitti: {len(channels)} kanal, {len(all_videos)} video, {len(sample)} orneklem videosu -> {OUT}/")
    if failed:
        print("Cozumlenemeyen kanallar:", *failed, sep="\n  ")


if __name__ == "__main__":
    main()
