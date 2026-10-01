"""Download scenes of the Ready-To-Train AI4Arctic Sea Ice Challenge Dataset (DTU / Figshare, no login needed).

Dataset: https://doi.org/10.11583/DTU.21316608 (version 3, 512 training scenes, ~110 MB each).
The server throttles each connection, so each file is fetched as several byte ranges in parallel,
then checked against the MD5 checksum published by Figshare.

Usage:
    uv run python scripts/download_ai4arctic.py --list                     # show the scenes the filter selects
    uv run python scripts/download_ai4arctic.py --max-scenes 3             # download the first 3 of them
    uv run python scripts/download_ai4arctic.py --names 20190505T102627_cis_prep.nc

Default selection: Canadian Ice Service (CIS) charts, cold season (Nov-May, dry snow).
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ARTICLE_API = "https://api.figshare.com/v2/articles/21316608"
OUT = Path(__file__).resolve().parent.parent / "data" / "ai4arctic"
COLD_MONTHS = {"11", "12", "01", "02", "03", "04", "05"}
HEADERS = {"User-Agent": "arctic-sea-ice-sar/0.1 (research download script)"}


def file_index():
    """List of {name, size, download_url, computed_md5} for every file in the dataset (cached locally)."""
    cache = OUT / "_index_rtt.json"
    if not cache.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(ARTICLE_API, headers=HEADERS)) as r:
            cache.write_bytes(r.read())
    return json.loads(cache.read_text())["files"]


def select(files, chart="cis", months=COLD_MONTHS):
    scenes = [f for f in files if f["name"].endswith("_prep.nc") and f"_{chart}_" in f["name"]]
    return sorted((f for f in scenes if f["name"][4:6] in months), key=lambda f: f["name"])


def signed_url(download_url):
    """Figshare redirects to a short-lived signed storage URL; resolve it once per file."""
    req = urllib.request.Request(download_url, headers={**HEADERS, "Range": "bytes=0-0"})
    with urllib.request.urlopen(req) as r:
        return r.geturl()


def fetch_range(url, start, end, part_path):
    req = urllib.request.Request(url, headers={**HEADERS, "Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=120) as r, open(part_path, "wb") as fh:
        while chunk := r.read(1 << 20):
            fh.write(chunk)
    got = part_path.stat().st_size
    if got != end - start + 1:
        raise IOError(f"{part_path.name}: expected {end - start + 1} bytes, got {got}")


def download(f, n_parts=8, retries=3):
    dest = OUT / f["name"]
    if dest.exists() and dest.stat().st_size == f["size"]:
        print(f"  have {f['name']}")
        return dest
    bounds = [(i * f["size"] // n_parts, (i + 1) * f["size"] // n_parts - 1) for i in range(n_parts)]
    parts = [OUT / f"{f['name']}.part{i}" for i in range(n_parts)]
    for attempt in range(1, retries + 1):
        try:
            url = signed_url(f["download_url"])
            todo = [(s, e, p) for (s, e), p in zip(bounds, parts) if not (p.exists() and p.stat().st_size == e - s + 1)]
            with ThreadPoolExecutor(n_parts) as pool:
                list(pool.map(lambda a: fetch_range(url, *a), todo))
            break
        except Exception as exc:  # network hiccup: keep finished parts, retry the rest
            print(f"  attempt {attempt} failed: {exc}", file=sys.stderr)
            if attempt == retries:
                raise
    md5 = hashlib.md5()
    with open(dest, "wb") as out:
        for p in parts:
            data = p.read_bytes()
            md5.update(data)
            out.write(data)
    for p in parts:
        p.unlink()
    if md5.hexdigest() != f["computed_md5"]:
        dest.unlink()
        raise IOError(f"{f['name']}: MD5 mismatch, file removed")
    print(f"  ok   {f['name']} ({f['size'] / 1e6:.0f} MB, MD5 verified)")
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="only list the selected scenes")
    ap.add_argument("--names", nargs="*", help="download exactly these file names")
    ap.add_argument("--max-scenes", type=int, default=None)
    ap.add_argument("--parts", type=int, default=8, help="parallel connections per file")
    args = ap.parse_args()

    files = file_index()
    chosen = [f for f in files if f["name"] in set(args.names)] if args.names else select(files)
    chosen = chosen[: args.max_scenes] if args.max_scenes else chosen
    print(f"{len(chosen)} scenes, {sum(f['size'] for f in chosen) / 1e9:.1f} GB")
    if args.list:
        for f in chosen:
            print(f"  {f['name']}  {f['size'] / 1e6:6.0f} MB")
        return
    for f in chosen:
        download(f, n_parts=args.parts)


if __name__ == "__main__":
    main()
