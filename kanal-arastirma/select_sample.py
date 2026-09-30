#!/usr/bin/env python3
"""Asama C: nihai kanal listesi icin video orneklemi secer (analyze.py ciktisini kullanir).

    python select_sample.py [--only final_channels.txt]

final_channels.txt: her satira bir kanal adi veya channel_id (verilmezse tum kanallar).
Kanal basina, olgun ve yeterince uzun videolardan: en iyi N_TOP, medyana en yakin N_MID,
en kotu N_LOW video. Cikti: out/sample.csv
"""
import sys
from pathlib import Path

from analyze import OUT, build, write_csv

MIN_SEC = 240            # orneklemde en az bu sure (Shorts ve cok kisa videolar disarida)
MAX_AGE_DAYS = 365       # son bu kadar gunun videolari
N_TOP, N_MID, N_LOW = 3, 2, 2


def pick(rows):
    pool = [r for r in rows if r["duration_sec"] >= MIN_SEC and not r["too_new"]
            and r["age_days"] <= MAX_AGE_DAYS and r["outlier_ratio"] != ""]
    if len(pool) <= N_TOP + N_MID + N_LOW:
        return [{**r, "sample_role": "all"} for r in pool]
    ranked = sorted(pool, key=lambda r: r["outlier_ratio"], reverse=True)
    top, low = ranked[:N_TOP], ranked[-N_LOW:]
    rest = [r for r in ranked if r not in top and r not in low]
    mid = sorted(rest, key=lambda r: abs(r["outlier_ratio"] - 1))[:N_MID]
    return [{**r, "sample_role": role} for role, g in (("top", top), ("mid", mid), ("low", low)) for r in g]


def main():
    only = None
    if "--only" in sys.argv:
        names = Path(sys.argv[sys.argv.index("--only") + 1]).read_text(encoding="utf-8").splitlines()
        only = {n.strip() for n in names if n.strip() and not n.startswith("#")}
    chans, vids, _ = build()
    keep = [c for c in chans if only is None or c["channel"] in only or c["channel_id"] in only]
    if only is not None:
        missing = only - {c["channel"] for c in keep} - {c["channel_id"] for c in keep}
        if missing:
            print("Listede olup veride bulunamayan:", *sorted(missing), sep="\n  ")
    sample = []
    for c in keep:
        picked = pick([v for v in vids if v["channel_id"] == c["channel_id"]])
        sample.extend(picked)
        print(f"{c['channel']}: {len(picked)} video")
    write_csv(OUT / "sample.csv", sample)
    print(f"\n{len(keep)} kanal, {len(sample)} video -> {OUT}/sample.csv")


if __name__ == "__main__":
    main()
