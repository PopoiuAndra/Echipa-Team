from __future__ import annotations

import httpx

from .config import GITHUB_TOKEN


class GitHubConnector:
    def __init__(self, token: str = GITHUB_TOKEN) -> None:
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def fetch_profile(self, username: str) -> dict:
        async with httpx.AsyncClient(timeout=15.0, headers=self.headers) as client:
            user_response = await client.get(f"https://api.github.com/users/{username}")
            user_response.raise_for_status()
            user = user_response.json()

            repos_response = await client.get(
                f"https://api.github.com/users/{username}/repos",
                params={"per_page": 100, "sort": "updated"},
            )
            repos_response.raise_for_status()
            repos = repos_response.json()

        languages: set[str] = set()
        topics: set[str] = set()
        for repo in repos:
            if repo.get("language"):
                languages.add(str(repo["language"]))
            topics.update(str(topic) for topic in repo.get("topics", []))

        return {
            "name": user.get("name") or username,
            "location": user.get("location"),
            "languages": sorted(languages),
            "topics": sorted(topics),
            "bio": user.get("bio"),
        }
