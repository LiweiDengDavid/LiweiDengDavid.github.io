import json
import os
from datetime import datetime, timezone
from pathlib import Path

from scholarly import scholarly


scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID", "").strip()
if not scholar_id:
    raise RuntimeError("GOOGLE_SCHOLAR_ID is required")

author = scholarly.search_author_id(scholar_id)
author = scholarly.fill(
    author,
    sections=["basics", "indices", "counts", "publications"],
)

if "citedby" not in author:
    raise RuntimeError("Google Scholar returned no citation count")

publications = author.get("publications", [])
author["publications"] = {
    publication["author_pub_id"]: publication
    for publication in publications
    if publication.get("author_pub_id")
}
author["updated"] = datetime.now(timezone.utc).isoformat()

output_dir = Path(__file__).resolve().parent / "results"
output_dir.mkdir(parents=True, exist_ok=True)

with (output_dir / "gs_data.json").open("w", encoding="utf-8") as outfile:
    json.dump(author, outfile, ensure_ascii=False)
    outfile.write("\n")

shields_io_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": str(author["citedby"]),
    "cacheSeconds": 300,
}
with (output_dir / "gs_data_shieldsio.json").open(
    "w", encoding="utf-8"
) as outfile:
    json.dump(shields_io_data, outfile, ensure_ascii=False)
    outfile.write("\n")

print(
    f"Fetched {author['citedby']} citations across "
    f"{len(author['publications'])} publications for {author.get('name', scholar_id)}."
)
