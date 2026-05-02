"""Per-show configuration loader.

Each podcast under `podcasts/<slug>/` has a `show.toml` file. This module is
the single way to read it from Python tooling (gen_tts.py, new_show.py, etc.).

Usage:
    from lib.show import load
    show = load("biomedical-agentic-ai")
    show.tts_primary  # -> {"provider": "mistral", "model": ..., "voice": ...}
    show.scripts_dir  # -> Path("podcasts/biomedical-agentic-ai/scripts")
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PODCASTS_DIR = REPO_ROOT / "podcasts"


@dataclass(frozen=True)
class Show:
    slug: str
    dir: Path
    config: dict

    @property
    def title(self) -> str:
        return self.config.get("title", self.slug)

    @property
    def podcast_slug(self) -> str:
        return self.config.get("podcast_slug", self.slug)

    @property
    def tts_primary(self) -> dict:
        return self.config.get("tts", {}).get("primary", {})

    @property
    def tts_fallback(self) -> dict | None:
        fb = self.config.get("tts", {}).get("fallback")
        return fb if fb else None

    def _path(self, key: str, default: str) -> Path:
        return self.dir / self.config.get("paths", {}).get(key, default)

    @property
    def episodes_dir(self) -> Path:
        return self._path("episodes", "episodes")

    @property
    def scripts_dir(self) -> Path:
        return self._path("scripts", "scripts")

    @property
    def logs_dir(self) -> Path:
        return self._path("logs", "logs")

    @property
    def feed_path(self) -> Path:
        return self._path("feed", "feed.xml")

    @property
    def prompt_path(self) -> Path:
        return self._path("prompt", "PROMPT.md")


def load(slug: str) -> Show:
    show_dir = PODCASTS_DIR / slug
    cfg_path = show_dir / "show.toml"
    if not cfg_path.exists():
        raise FileNotFoundError(f"show config not found: {cfg_path}")
    with cfg_path.open("rb") as f:
        cfg = tomllib.load(f)
    return Show(slug=slug, dir=show_dir, config=cfg)


def list_slugs() -> list[str]:
    if not PODCASTS_DIR.exists():
        return []
    return sorted(
        p.name for p in PODCASTS_DIR.iterdir()
        if p.is_dir() and (p / "show.toml").exists()
    )
