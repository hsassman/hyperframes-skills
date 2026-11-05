#!/usr/bin/env python3
"""
Search Pexels and/or Pixabay video APIs for stock footage matching a query.

Usage:
    python search_stock.py --query "city skyline sunset timelapse" --source pexels --per-page 10
    python search_stock.py --query "ocean waves" --source pixabay --per-page 10
    python search_stock.py --query "ocean waves" --source both --per-page 5

Requires environment variables:
    PEXELS_API_KEY
    PIXABAY_API_KEY
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse


def search_pexels(query: str, per_page: int):
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("PEXELS_API_KEY not set -- skipping Pexels search.", file=sys.stderr)
        return []

    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": "landscape"}
    )
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())

    results = []
    for video in data.get("videos", []):
        # pick the highest-resolution HD/SD file link available
        files = sorted(
            video.get("video_files", []),
            key=lambda f: (f.get("width") or 0) * (f.get("height") or 0),
            reverse=True,
        )
        best_file = files[0] if files else None
        results.append(
            {
                "source": "pexels",
                "id": video["id"],
                "url": video["url"],
                "duration_sec": video.get("duration"),
                "width": video.get("width"),
                "height": video.get("height"),
                "photographer": video.get("user", {}).get("name"),
                "photographer_url": video.get("user", {}).get("url"),
                "download_url": best_file["link"] if best_file else None,
                "license": "Pexels License (free for commercial use, no attribution required)",
            }
        )
    return results


def search_pixabay(query: str, per_page: int):
    api_key = os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("PIXABAY_API_KEY not set -- skipping Pixabay search.", file=sys.stderr)
        return []

    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": api_key, "q": query, "per_page": max(per_page, 3)}  # pixabay min per_page is 3
    )
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())

    results = []
    for hit in data.get("hits", [])[:per_page]:
        videos = hit.get("videos", {})
        # prefer large > medium > small
        best = videos.get("large") or videos.get("medium") or videos.get("small")
        results.append(
            {
                "source": "pixabay",
                "id": hit["id"],
                "url": hit.get("pageURL"),
                "duration_sec": hit.get("duration"),
                "width": best.get("width") if best else None,
                "height": best.get("height") if best else None,
                "photographer": hit.get("user"),
                "photographer_url": f"https://pixabay.com/users/{hit.get('user')}-{hit.get('user_id')}/",
                "download_url": best.get("url") if best else None,
                "license": "Pixabay Content License (free for commercial use, no attribution required)",
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--source", choices=["pexels", "pixabay", "both"], default="both")
    parser.add_argument("--per-page", type=int, default=10)
    args = parser.parse_args()

    results = []
    if args.source in ("pexels", "both"):
        results.extend(search_pexels(args.query, args.per_page))
    if args.source in ("pixabay", "both"):
        results.extend(search_pixabay(args.query, args.per_page))

    if not results:
        print(
            f"No results found for query '{args.query}' (or required API keys are missing). "
            "Try broadening the query or check PEXELS_API_KEY / PIXABAY_API_KEY are set.",
            file=sys.stderr,
        )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
