import requests
import logging
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import json

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

    def _get_fallback_profile(self):
        """Return fallback data when API is unavailable"""
        return {
            "login": self.username,
            "name": "Vasile Ovidiu Ichim",
            "bio": "CTO & Co-founder at Valerdat building AI-powered purchasing assistant",
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
