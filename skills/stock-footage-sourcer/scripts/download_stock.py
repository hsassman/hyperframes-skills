#!/usr/bin/env python3
"""
Download a selected stock video clip and write a license metadata sidecar
JSON file alongside it. Always run this rather than downloading manually with
curl/wget, so every clip in the project has a paper trail of its source and
license.

Usage:
    python download_stock.py --url "<direct_video_file_url>" --source pexels \
        --id "12345" --output footage/clip_042.mp4 \
        --page-url "https://www.pexels.com/video/12345/" \
        --photographer "Jane Doe" --license "Pexels License"
"""
import argparse
import datetime
import json
import os
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Direct downloadable video file URL")
    parser.add_argument("--source", required=True, choices=["pexels", "pixabay", "storyblocks", "envato"])
    parser.add_argument("--id", required=True, help="Source platform's ID for this asset")
    parser.add_argument("--output", required=True, help="Local output path for the video file")
    parser.add_argument("--page-url", default=None, help="Original listing/page URL for the asset")
    parser.add_argument("--photographer", default=None, help="Creator/photographer name, if available")
    parser.add_argument("--license", default=None, help="License name/description")
    parser.add_argument("--query", default=None, help="Search query that surfaced this result, for traceability")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    print(f"Downloading {args.url} -> {args.output} ...")
    urllib.request.urlretrieve(args.url, args.output)

    sidecar_path = os.path.splitext(args.output)[0] + ".license.json"
    metadata = {
        "downloaded_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "source": args.source,
        "source_id": args.id,
        "source_page_url": args.page_url,
        "download_url": args.url,
        "photographer": args.photographer,
        "license": args.license,
        "search_query": args.query,
        "local_file": os.path.abspath(args.output),
    }
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Wrote license metadata sidecar -> {sidecar_path}")


if __name__ == "__main__":
    main()
