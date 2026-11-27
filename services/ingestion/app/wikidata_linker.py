from __future__ import annotations

import httpx


class WikidataLinker:
    def __init__(self) -> None:
        self.cache: dict[str, str | None] = {}

    async def link(self, label: str) -> str | None:
        key = label.strip().casefold()
        if key in self.cache:
            return self.cache[key]

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://www.wikidata.org/w/api.php",
                params={
                    "action": "wbsearchentities",
                    "search": label,
                    "language": "en",
                    "format": "json",
                    "limit": 1,
                },
            )
            response.raise_for_status()
            matches = response.json().get("search", [])

        qid = matches[0]["id"] if matches else None
        self.cache[key] = qid
        return qid
