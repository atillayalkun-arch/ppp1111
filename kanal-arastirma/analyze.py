#!/usr/bin/env python3
"""Asama B: ham veriden tum metrikleri hesaplar, kanallari gruplara dizer, kota raporu verir.

API cagirmaz (data/raw/ okur). Esikleri asagida degistirip istedigin kadar tekrar calistir.

    python analyze.py

Cikti (out/):
  channels_full.csv   kanal basina tum alanlar + hesaplanan metrikler + bayraklar + bucket
  videos_full.csv     tum videolar (Shorts dahil), tum alanlar + outlier orani
  group_report.txt    bucket bazinda kanal listesi ve hedef kota karsilastirmasi
  channel_briefs.json AI'ya (Gemini vb.) verilecek kompakt ozet
"""
import csv
import json
import re
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("out")

# ---- esikler (istedigin gibi degistir) ----
SHORT_MAX_SEC = 180       # bu sureye kadar (dahil) "short" sayilir
MATURE_DAYS = 14          # bundan yeni videolar outlier hesabina girmez
WINDOW_DAYS = 365         # outlier taban penceresi
STALLED_DAYS = 60         # son uzun videodan beri bu kadar gun -> durmus
BIG_SUBS = 100_000
LOW_TRACTION_MEDIAN = 2000   # >=5 uzun video olup medyan izlenme bunun altindaysa "zayif"
TARGETS = {"core-big": 5, "core-rising": 7, "core-stalled-or-weak": 4, "neighbor": 14, "global": 7}

JP = re.compile(r"[぀-ヿ一-鿿]")


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_duration(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def med(xs):
    xs = list(xs)
    return statistics.median(xs) if xs else ""


def topics(obj):
    return "|".join(u.rsplit("/", 1)[-1] for u in obj.get("topicDetails", {}).get("topicCategories", []))


# ------------------------------------------------------------ videolar ----
def video_flat(v, now):
    sn, st, cd = v["snippet"], v.get("statistics", {}), v.get("contentDetails", {})
    pub = parse_ts(sn["publishedAt"])
    age_h = max((now - pub).total_seconds() / 3600, 1)
    dur = parse_duration(cd.get("duration"))
    views = int(st.get("viewCount", 0))
    likes = int(st["likeCount"]) if "likeCount" in st else None
    comments = int(st["commentCount"]) if "commentCount" in st else None
    thumbs = sn.get("thumbnails", {})
    thumb = next((thumbs[k]["url"] for k in ("maxres", "standard", "high", "medium") if k in thumbs), "")
    tags = sn.get("tags", [])
    text = sn["title"] + " " + sn.get("description", "")
    return {
        "video_id": v["id"],
        "url": f"https://www.youtube.com/watch?v={v['id']}",
        "title": sn["title"],
        "published": pub.date().isoformat(),
        "age_days": round(age_h / 24, 1),
        "duration_sec": dur,
        "duration_min": round(dur / 60, 1),
        "is_short": dur <= SHORT_MAX_SEC,
        "shorts_hashtag": "#shorts" in text.lower(),
        "views": views,
        "likes": "" if likes is None else likes,
        "comments": "" if comments is None else comments,
        "likes_hidden": likes is None,
        "comments_disabled": comments is None,
        "like_rate": round((likes or 0) / views, 4) if views else 0,
        "comment_rate": round((comments or 0) / views, 5) if views else 0,
        "engagement": round(((likes or 0) + (comments or 0)) / views, 4) if views else 0,
        "vph_avg": round(views / age_h, 1),
        "views_per_day": round(views / max(age_h / 24, 1), 1),
        "category_id": sn.get("categoryId", ""),
        "default_language": sn.get("defaultLanguage", ""),
        "default_audio_language": sn.get("defaultAudioLanguage", ""),
        "tag_count": len(tags),
        "tags": "|".join(tags),
        "description_len": len(sn.get("description", "")),
        "description_head": " ".join(sn.get("description", "").split())[:300],
        "has_caption": cd.get("caption", ""),
        "definition": cd.get("definition", ""),
        "licensed_content": cd.get("licensedContent", ""),
        "made_for_kids": v.get("status", {}).get("madeForKids", ""),
        "privacy": v.get("status", {}).get("privacyStatus", ""),
        "embeddable": v.get("status", {}).get("embeddable", ""),
        "was_live": "liveStreamingDetails" in v,
        "paid_placement": v.get("paidProductPlacementDetails", {}).get("hasPaidProductPlacement", ""),
        "topics": topics(v),
        "thumbnail": thumb,
        "_pub": pub,
    }


def add_outliers(rows):
    """Uzun ve short videolar kendi icinde: olgun videolarin medyanina oran."""
    meds = {}
    for kind in (False, True):
        grp = [r for r in rows if r["is_short"] == kind and r["age_days"] >= MATURE_DAYS]
        win = [r for r in grp if r["age_days"] <= WINDOW_DAYS]
        target = win if len(win) >= 5 else grp
        m = statistics.median(r["views"] for r in target) if target else 0
        meds["short" if kind else "long"] = m
        for r in target:
            r["outlier_ratio"] = round(r["views"] / m, 2) if m else ""
    for r in rows:
        r["too_new"] = r["age_days"] < MATURE_DAYS
        r.setdefault("outlier_ratio", "")
    return meds


# -------------------------------------------------------------- kanallar ----
def bucket(cls, flags, subs):
    if cls == "neighbor" or cls == "global":
        return cls
    if cls != "core":
        return cls or "unlabeled"
    if "stalled" in flags or "weak" in flags:
        return "core-stalled-or-weak"
    if subs >= BIG_SUBS:
        return "core-big"
    if "new_channel_first_video" in flags:
        return "core-rising"
    return "core-other"


def channel_row(raw, rows, meds, now):
    meta, ch, pls = raw["meta"], raw["channel"], raw.get("playlists", [])
    sn, st = ch["snippet"], ch.get("statistics", {})
    br = ch.get("brandingSettings", {}).get("channel", {})
    created = parse_ts(sn["publishedAt"])
    longs = [r for r in rows if not r["is_short"]]
    shorts = [r for r in rows if r["is_short"]]
    pubs = [r["_pub"] for r in rows]
    first, last = (min(pubs), max(pubs)) if pubs else (None, None)
    last_long = max((r["_pub"] for r in longs), default=None)
    subs = int(st.get("subscriberCount", 0))
    within = lambda rs, d: [r for r in rs if r["age_days"] <= d]
    long12, long90, short12 = within(longs, 365), within(longs, 90), within(shorts, 365)
    span_weeks = max(min((now - first).days, 365), 7) / 7 if first else 1
    active_weeks = len({int(r["age_days"] // 7) for r in long90 if r["age_days"] <= 84})
    mature_ratios = [r["outlier_ratio"] for r in longs if r["outlier_ratio"] != ""]
    tot_views = sum(r["views"] for r in rows)
    long_views = sum(r["views"] for r in longs)
    days_since_long = (now - last_long).days if last_long else ""
    titles = [r["title"] for r in rows]
    langs = Counter(r["default_audio_language"] or r["default_language"] for r in rows if r["default_audio_language"] or r["default_language"])
    top_pls = sorted(pls, key=lambda p: p["contentDetails"].get("itemCount", 0), reverse=True)[:10]

    flags = []
    if st.get("hiddenSubscriberCount"):
        flags.append("hidden_subs")
    if last_long is None or (now - last_long).days > STALLED_DAYS:
        flags.append("stalled")
    if len(longs) < 5:
        flags.append("few_long_videos")
    if len(longs) >= 5 and med(r["views"] for r in longs) < LOW_TRACTION_MEDIAN:
        flags.append("weak")
    if first and (now - first).days <= 365:
        flags.append("new_channel_first_video")
    if meta["class"] != "global" and titles and sum(bool(JP.search(t)) for t in titles) / len(titles) < 0.5:
        flags.append("titles_not_japanese")
    if not meta["class"]:
        flags.append("no_class_label")

    return {
        "class": meta["class"], "note": meta["note"],
        "bucket": bucket(meta["class"], flags, subs),
        "channel": sn["title"], "handle": sn.get("customUrl", ""),
        "url": f"https://www.youtube.com/channel/{ch['id']}", "channel_id": ch["id"],
        "country": sn.get("country", br.get("country", "")),
        "default_language": sn.get("defaultLanguage", br.get("defaultLanguage", "")),
        "video_languages": "|".join(f"{k}:{v}" for k, v in langs.most_common(3)),
        "created": created.date().isoformat(),
        "first_video": first.date().isoformat() if first else "",
        "created_to_first_video_days": (first - created).days if first else "",
        "channel_age_days": (now - created).days,
        "first_video_age_days": (now - first).days if first else "",
        "last_video": last.date().isoformat() if last else "",
        "last_long_video": last_long.date().isoformat() if last_long else "",
        "days_since_last_long": days_since_long,
        "subs": subs, "subs_hidden": bool(st.get("hiddenSubscriberCount")),
        "total_views": int(st.get("viewCount", 0)),
        "total_videos_api": int(st.get("videoCount", 0)),
        "videos_collected": len(rows), "long_total": len(longs), "short_total": len(shorts),
        "long_12m": len(long12), "short_12m": len(short12),
        "long_per_week_12m": round(len(long12) / span_weeks, 2),
        "long_per_week_90d": round(len(long90) / (90 / 7), 2),
        "active_weeks_of_last_12": active_weeks,
        "short_share_of_videos": round(len(shorts) / len(rows), 2) if rows else "",
        "short_share_of_views": round(1 - long_views / tot_views, 2) if tot_views else "",
        "median_duration_min_long": med(r["duration_min"] for r in longs),
        "median_views_long": med(r["views"] for r in longs),
        "median_views_long_12m": med(r["views"] for r in long12),
        "median_views_short": med(r["views"] for r in shorts),
        "mean_views_long": round(long_views / len(longs)) if longs else "",
        "median_views_per_sub_long": round(med(r["views"] for r in longs) / subs, 3) if longs and subs else "",
        "median_engagement_long": med(r["engagement"] for r in longs),
        "median_likes_long": med(r["likes"] for r in longs if r["likes"] != ""),
        "median_comments_long": med(r["comments"] for r in longs if r["comments"] != ""),
        "top1_share_of_long_views": round(max(r["views"] for r in longs) / long_views, 2) if long_views else "",
        "max_outlier_ratio_long": max(mature_ratios, default=""),
        "share_outliers_2x_long": round(sum(x >= 2 for x in mature_ratios) / len(mature_ratios), 2) if mature_ratios else "",
        "views_last_90d": sum(r["views"] for r in rows if r["age_days"] <= 90),
        "comments_disabled_share": round(sum(r["comments_disabled"] for r in longs) / len(longs), 2) if longs else "",
        "avg_tag_count": round(sum(r["tag_count"] for r in rows) / len(rows), 1) if rows else "",
        "playlist_count": len(pls),
        "top_playlists": " | ".join(f"{p['snippet']['title']} ({p['contentDetails'].get('itemCount', 0)})" for p in top_pls),
        "keywords": " ".join(br.get("keywords", "").split())[:300],
        "topics": topics(ch),
        "made_for_kids": ch.get("status", {}).get("madeForKids", ""),
        "flags": ",".join(flags),
        "description": " ".join(sn.get("description", "").split())[:400],
    }


def brief(crow, rows):
    longs = sorted((r for r in rows if not r["is_short"]), key=lambda r: r["views"], reverse=True)
    pick = lambda rs: [{"title": r["title"], "views": r["views"], "min": r["duration_min"],
                        "age_days": r["age_days"], "outlier": r["outlier_ratio"]} for r in rs]
    keys = ("class", "note", "bucket", "channel", "handle", "created", "first_video", "subs", "flags",
            "long_per_week_12m", "median_duration_min_long", "median_views_long", "max_outlier_ratio_long",
            "short_share_of_views", "top_playlists", "keywords", "description")
    return {k: crow[k] for k in keys} | {
        "top_titles": pick(longs[:10]),
        "bottom_titles": pick(longs[-5:] if len(longs) > 10 else []),
        "recent_titles": pick(sorted((r for r in rows if not r["is_short"]), key=lambda r: r["age_days"])[:5]),
    }


# ------------------------------------------------------------------ ana ----
def build():
    chans, vids, briefs = [], [], []
    for p in sorted(RAW.glob("*.json")):
        raw = json.loads(p.read_text(encoding="utf-8"))
        now = parse_ts(raw["meta"]["collected_at"])
        rows = [video_flat(v, now) for v in raw["videos"]]
        meds = add_outliers(rows)
        crow = channel_row(raw, rows, meds, now)
        for r in rows:
            r.update(channel=crow["channel"], channel_id=crow["channel_id"], bucket=crow["bucket"])
        chans.append(crow)
        vids.extend(rows)
        briefs.append(brief(crow, rows))
    order = {b: i for i, b in enumerate(["own", *TARGETS, "core-other"])}
    chans.sort(key=lambda c: (order.get(c["bucket"], 99), -c["subs"]))
    return chans, vids, briefs


def write_csv(path, rows):
    if rows:
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if not k.startswith("_")], extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)


def report(chans):
    lines = ["KOTA KONTROLU (hedef / mevcut)"]
    counts = Counter(c["bucket"] for c in chans)
    for b, t in TARGETS.items():
        have = counts.get(b, 0)
        lines.append(f"  {b:24s} {t:>3} / {have:<3} {'OK' if have >= t else 'EKSIK ' + str(t - have)}")
    for b in counts:
        if b not in TARGETS:
            lines.append(f"  {b:24s}  -  / {counts[b]:<3} (hedefsiz)")
    lines.append("")
    for b in sorted(counts, key=lambda x: order_key(x)):
        lines.append(f"== {b} ({counts[b]})")
        for c in (c for c in chans if c["bucket"] == b):
            lines.append(f"  - {c['channel']} | abone {c['subs']:,} | ilk video {c['first_video']} | "
                         f"uzun/12ay {c['long_12m']} | medyan izl. {c['median_views_long']} | "
                         f"max outlier {c['max_outlier_ratio_long']} | {c['flags'] or '-'}")
        lines.append("")
    return "\n".join(lines)


def order_key(b):
    return (["own", *TARGETS, "core-other"].index(b) if b in ["own", *TARGETS, "core-other"] else 99)


def main():
    OUT.mkdir(exist_ok=True)
    chans, vids, briefs = build()
    if not chans:
        raise SystemExit("data/raw/ bos. Once collect.py calistir.")
    write_csv(OUT / "channels_full.csv", chans)
    write_csv(OUT / "videos_full.csv", vids)
    (OUT / "channel_briefs.json").write_text(json.dumps(briefs, ensure_ascii=False, indent=1), encoding="utf-8")
    txt = report(chans)
    (OUT / "group_report.txt").write_text(txt, encoding="utf-8")
    print(txt)
    print(f"\n{len(chans)} kanal, {len(vids)} video -> {OUT}/")


if __name__ == "__main__":
    main()
