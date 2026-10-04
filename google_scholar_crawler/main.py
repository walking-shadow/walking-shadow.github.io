import json
import os
import sys
from datetime import datetime
from pathlib import Path

from scholarly import scholarly

SCHOLAR_ID = os.environ.get("GOOGLE_SCHOLAR_ID", "o-GZavgAAAAJ")
# Resolve against this file so the script works from any working directory.
RESULTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "results"


def main() -> int:
    author: dict = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    if 'citedby' not in author:
        # Google Scholar blocked or throttled the request; keep the previous results.
        print("No citation count returned by Google Scholar, keeping existing data.", file=sys.stderr)
        return 1

    author['updated'] = str(datetime.now())
    author['publications'] = {v['author_pub_id']: v for v in author['publications']}
    print(f"{author['name']}: {author['citedby']} citations, {len(author['publications'])} publications")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_DIR / 'gs_data.json', 'w', encoding='utf-8') as outfile:
        json.dump(author, outfile, ensure_ascii=False, default=str)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": f"{author['citedby']}",
    }
    with open(RESULTS_DIR / 'gs_data_shieldsio.json', 'w', encoding='utf-8') as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
