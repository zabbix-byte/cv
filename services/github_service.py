import base64
import json
import logging
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GitHubService:
    """Service to fetch GitHub profile and repository data"""

    BASE_URL = "https://api.github.com"
    CACHE_TIMEOUT = 3600  # 1 hour cache

    def __init__(self, username="zabbix-byte"):
        self.username = username
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CV-Django-App",
        }

        # Add GitHub token if available (for higher rate limits)
        github_token = getattr(settings, "GITHUB_TOKEN", None)
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def _make_request(self, endpoint):
        """Make a request to GitHub API with error handling"""
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                logger.warning(f"GitHub API rate limit exceeded for {endpoint}")
                return None
            elif response.status_code == 404:
                logger.warning(f"GitHub resource not found: {endpoint}")
                return None
            else:
                logger.error(f"GitHub API error {response.status_code} for {endpoint}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request error when fetching {endpoint}: {str(e)}")
            return None

    def get_user_profile(self):
        """Fetch user profile information"""
        cache_key = f"github_profile_{self.username}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        profile_data = self._make_request(f"users/{self.username}")

        if profile_data:
            # Extract relevant information
            processed_data = {
                "login": profile_data.get("login"),
                "name": profile_data.get("name"),
                "bio": profile_data.get("bio"),
                "location": profile_data.get("location"),
                "public_repos": profile_data.get("public_repos", 0),
                "followers": profile_data.get("followers", 0),
                "following": profile_data.get("following", 0),
                "created_at": profile_data.get("created_at"),
                "updated_at": profile_data.get("updated_at"),
                "avatar_url": profile_data.get("avatar_url"),
                "html_url": profile_data.get("html_url"),
                "company": profile_data.get("company"),
                "blog": profile_data.get("blog"),
                "email": profile_data.get("email"),
                "hireable": profile_data.get("hireable"),
            }

            # Cache the processed data
            cache.set(cache_key, processed_data, self.CACHE_TIMEOUT)
            return processed_data

        return self._get_fallback_profile()

    def get_repositories(self, per_page=30, sort="updated"):
        """Fetch user repositories"""
        cache_key = f"github_repos_{self.username}_{per_page}_{sort}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        repos_data = self._make_request(
            f"users/{self.username}/repos?per_page={per_page}&sort={sort}"
        )

        if repos_data:
            # Process repositories data
            processed_repos = []
            seen_repo_names = set()  # Track repository names to avoid duplicates

            for repo in repos_data:
                repo_name = repo.get("name")

                # Skip duplicates and forks for main display
                if repo_name in seen_repo_names or repo.get("fork", False):
                    continue

                seen_repo_names.add(repo_name)

                processed_repo = {
                    "name": repo_name,
                    "description": repo.get("description"),
                    "html_url": repo.get("html_url"),
                    "language": repo.get("language"),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "watchers_count": repo.get("watchers_count", 0),
                    "size": repo.get("size", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "private": repo.get("private", False),
                    "fork": repo.get("fork", False),
                    "archived": repo.get("archived", False),
                    "topics": repo.get("topics", []),
                }
                processed_repos.append(processed_repo)

            # Sort by stargazers count for better display (most popular first)
            processed_repos.sort(key=lambda x: x["stargazers_count"], reverse=True)

            # Cache the processed data
            cache.set(cache_key, processed_repos, self.CACHE_TIMEOUT)
            return processed_repos

        return []

    def get_repository_languages(self):
        """Fetch languages used across all repositories"""
        cache_key = f"github_languages_{self.username}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        repos = self.get_repositories()
        language_stats = {}

        for repo in repos:
            if repo["language"] and not repo["fork"]:  # Don't count forked repos
                lang = repo["language"]
                if lang in language_stats:
                    language_stats[lang] += 1
                else:
                    language_stats[lang] = 1

        # Sort by usage count
        sorted_languages = sorted(
            language_stats.items(), key=lambda x: x[1], reverse=True
        )

        # Cache the data
        cache.set(cache_key, sorted_languages, self.CACHE_TIMEOUT)
        return sorted_languages

    def get_user_events(self, per_page=10):
        """Fetch recent user activity events"""
        cache_key = f"github_events_{self.username}_{per_page}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        events_data = self._make_request(
            f"users/{self.username}/events?per_page={per_page}"
        )

        if events_data:
            # Process events data
            processed_events = []
            for event in events_data:
                processed_event = {
                    "type": event.get("type"),
                    "repo_name": event.get("repo", {}).get("name"),
                    "created_at": event.get("created_at"),
                    "public": event.get("public", True),
                }

                # Add event-specific data
                if event.get("payload"):
                    payload = event["payload"]
                    if event["type"] == "PushEvent":
                        processed_event["commits"] = len(payload.get("commits", []))
                        processed_event["ref"] = payload.get("ref", "").replace(
                            "refs/heads/", ""
                        )
                    elif event["type"] == "CreateEvent":
                        processed_event["ref_type"] = payload.get("ref_type")
                        processed_event["ref"] = payload.get("ref")
                    elif event["type"] == "IssuesEvent":
                        processed_event["action"] = payload.get("action")
                    elif event["type"] == "PullRequestEvent":
                        processed_event["action"] = payload.get("action")

                processed_events.append(processed_event)

            # Cache the processed data
            cache.set(cache_key, processed_events, self.CACHE_TIMEOUT)
            return processed_events

        return []

    def get_comprehensive_stats(self):
        """Get comprehensive GitHub statistics"""
        profile = self.get_user_profile()
        repos = self.get_repositories()
        languages = self.get_repository_languages()
        events = self.get_user_events()

        # Calculate additional stats
        total_stars = sum(
            repo["stargazers_count"] for repo in repos if not repo["fork"]
        )
        total_forks = sum(repo["forks_count"] for repo in repos if not repo["fork"])

        # Get recent activity summary
        recent_activity = []
        for event in events[:5]:  # Last 5 events
            activity_text = self._format_activity(event)
            if activity_text:
                recent_activity.append(
                    {
                        "text": activity_text,
                        "created_at": event["created_at"],
                        "repo_name": event["repo_name"],
                    }
                )

        return {
            "profile": profile,
            "repositories": repos,
            "languages": languages,
            "recent_activity": recent_activity,
            "stats": {
                "total_repos": len([r for r in repos if not r["fork"]]),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "followers": profile.get("followers", 0) if profile else 0,
                "following": profile.get("following", 0) if profile else 0,
            },
        }

    def get_card_metrics(self):
        """Totals GitHub's profile UI does not surface (stars/forks across work)."""
        cache_key = f"github_card_metrics_v1_{self.username}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        profile = self.get_user_profile() or {}
        repos = self.get_repositories(per_page=100) or []
        own = [repo for repo in repos if not repo.get("fork")]
        lang_counts = {}
        for repo in own:
            lang = repo.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        langs = [name for name, _ in sorted(lang_counts.items(), key=lambda item: -item[1])[:4]]

        github_year = None
        created = profile.get("created_at") or ""
        if len(created) >= 4 and created[:4].isdigit():
            github_year = int(created[:4])

        payload = {
            "stars": sum(repo.get("stargazers_count") or 0 for repo in own),
            "forks": sum(repo.get("forks_count") or 0 for repo in own),
            "langs": langs,
            "github_year": github_year,
            "years_coding": 13,
        }
        cache.set(cache_key, payload, self.CACHE_TIMEOUT)
        return payload

    def _format_activity(self, event):
        """Format activity event into readable text"""
        event_type = event.get("type")
        repo_name = (
            event.get("repo_name", "").split("/")[-1] if event.get("repo_name") else ""
        )

        if event_type == "PushEvent":
            ref = event.get("ref", "main")
            commits = event.get("commits", 0)
            return f"Pushed {commits} commit{'s' if commits != 1 else ''} to {ref} in {repo_name}"
        elif event_type == "CreateEvent":
            ref_type = event.get("ref_type", "repository")
            return f"Created {ref_type} {repo_name}"
        elif event_type == "IssuesEvent":
            action = event.get("action", "updated")
            return f"{action.capitalize()} issue in {repo_name}"
        elif event_type == "PullRequestEvent":
            action = event.get("action", "updated")
            return f"{action.capitalize()} pull request in {repo_name}"
        elif event_type == "WatchEvent":
            return f"Starred {repo_name}"
        elif event_type == "ForkEvent":
            return f"Forked {repo_name}"

        return None

    PINNED_REPOS = (
        "PyPulse",
        "ztdriver",
        "DiscordEasyCloner",
        "ztui",
        "zt_cs_cheat",
        "NFT-Generator",
    )

    def get_pinned_repos(self):
        cache_key = f"github_pinned_{self.username}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        pinned = []
        token = getattr(settings, "GITHUB_TOKEN", None)
        if token:
            query = """
            query ($login: String!) {
              user(login: $login) {
                pinnedItems(first: 6, types: REPOSITORY) {
                  nodes {
                    ... on Repository {
                      name
                      description
                      url
                      stargazerCount
                      forkCount
                      isArchived
                      primaryLanguage { name }
                    }
                  }
                }
              }
            }
            """
            try:
                response = requests.post(
                    "https://api.github.com/graphql",
                    json={"query": query, "variables": {"login": self.username}},
                    headers={
                        "Authorization": f"bearer {token}",
                        "User-Agent": "CV-Django-App",
                    },
                    timeout=10,
                )
                payload = response.json()
                nodes = (
                    ((payload.get("data") or {}).get("user") or {})
                    .get("pinnedItems", {})
                    .get("nodes")
                    or []
                )
                for node in nodes:
                    if not node or not node.get("name"):
                        continue
                    pinned.append(
                        {
                            "name": node["name"],
                            "description": node.get("description") or "",
                            "html_url": node.get("url"),
                            "language": (node.get("primaryLanguage") or {}).get("name") or "",
                            "stargazers_count": node.get("stargazerCount", 0),
                            "forks_count": node.get("forkCount", 0),
                            "archived": node.get("isArchived", False),
                        }
                    )
            except Exception:
                logger.warning("GitHub GraphQL pinned repos failed", exc_info=True)

        if not pinned:
            repos = {repo["name"]: repo for repo in self.get_repositories()}
            for name in self.PINNED_REPOS:
                if name in repos:
                    pinned.append(repos[name])

        cache.set(cache_key, pinned, self.CACHE_TIMEOUT)
        return pinned

    def get_contributions(self):
        cache_key = f"github_contrib_v1_{self.username}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        empty = {"total": 0, "weeks": []}
        try:
            response = requests.get(
                f"https://github-contributions-api.jogruber.de/v4/{self.username}?y=last",
                timeout=8,
            )
            payload = response.json()
        except Exception:
            cache.set(cache_key, empty, 60 * 15)
            return empty

        contribs = payload.get("contributions") or []
        totals = payload.get("total") or {}
        total = sum(totals.values()) if isinstance(totals, dict) else 0
        by_date = {}
        for row in contribs:
            day = row.get("date")
            if not day:
                continue
            by_date[day] = {
                "date": day,
                "count": int(row.get("count") or 0),
                "level": int(row.get("level") or 0),
            }

        today = datetime.utcnow().date()
        days_since_sunday = (today.weekday() + 1) % 7
        this_sunday = today - timedelta(days=days_since_sunday)
        start = this_sunday - timedelta(weeks=52)
        weeks = []
        for week_i in range(53):
            week = []
            for day_i in range(7):
                day = start + timedelta(days=week_i * 7 + day_i)
                info = by_date.get(
                    day.isoformat(),
                    {"date": day.isoformat(), "count": 0, "level": 0},
                )
                week.append(info)
            weeks.append(week)

        data = {"total": total, "weeks": weeks}
        cache.set(cache_key, data, self.CACHE_TIMEOUT)
        return data

    def get_avatar_data_uri(self, url):
        if not url:
            return ""
        cache_key = f"github_avatar_{self.username}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        uri = ""
        try:
            response = requests.get(
                url, timeout=6, headers={"User-Agent": "CV-Django-App"}
            )
            if response.status_code == 200 and response.content:
                mime = (response.headers.get("content-type") or "image/jpeg").split(";")[0]
                if mime not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
                    mime = "image/jpeg"
                uri = "data:{};base64,{}".format(
                    mime, base64.b64encode(response.content).decode("ascii")
                )
        except Exception:
            uri = ""
        cache.set(cache_key, uri, 60 * 60 * 12)
        return uri

    def get_widget_payload(self):
        stats = self.get_comprehensive_stats()
        contrib = self.get_contributions()
        pinned = self.get_pinned_repos()
        languages = (stats.get("languages") or [])[:5]
        lang_total = sum(count for _, count in languages) or 1
        profile = stats.get("profile") or self._get_fallback_profile()
        return {
            "profile": profile,
            "stats": stats.get("stats") or {},
            "pinned": pinned[:6],
            "languages": [
                {
                    "name": name,
                    "count": count,
                    "pct": round(100 * count / lang_total),
                }
                for name, count in languages
            ],
            "contrib_total": contrib.get("total") or 0,
            "weeks": contrib.get("weeks") or [],
            "avatar_data": self.get_avatar_data_uri(profile.get("avatar_url")),
        }

    def _get_fallback_profile(self):
        """Return fallback data when API is unavailable"""
        return {
            "login": self.username,
            "name": "Vasile Ovidiu Ichim",
            "bio": "Supply software by day, cracking games by night",
            "location": "Barcelona, Spain",
            "public_repos": 0,
            "followers": 0,
            "following": 0,
            "created_at": None,
            "updated_at": None,
            "avatar_url": None,
            "html_url": f"https://github.com/{self.username}",
            "company": "Valerdat",
            "blog": None,
            "email": None,
            "hireable": True,
        }
