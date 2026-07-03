"""Thin bridge from Agent OS into the NAC SDK. Contains NO filmmaking logic -
every function here is a direct passthrough to nac.Studio (E:\\nth-absolute-cinema).
Agent OS must never import engine.* directly; this file is the only permitted door.

Covers the original six pipeline actions plus Checkpoint C.5's director-validation
additions (status/regenerate/review/import-asset), since Studio grew those methods
before this bridge was written. Every function signature here mirrors a Studio method
1:1 - if Studio's public API changes, this file changes to match, never the other
way around."""
from __future__ import annotations

from pathlib import Path

from nac import Studio

_studio: Studio | None = None


def _get_studio() -> Studio:
    global _studio
    if _studio is None:
        _studio = Studio()
    return _studio


def launch_nac_project(idea_text: str, target_runtime_minutes: int = 15) -> str:
    return _get_studio().create_project(idea_text, target_runtime_minutes=target_runtime_minutes)


def generate_story(project_id: str) -> str:
    return _get_studio().generate_story(project_id)


def generate_screenplay(project_id: str) -> str:
    return _get_studio().generate_screenplay(project_id)


def generate_audio(project_id: str) -> Path:
    return _get_studio().generate_audio(project_id)


def generate_prompt(project_id: str) -> str:
    return _get_studio().generate_prompt(project_id)


def export_project(project_id: str, out_dir: str) -> Path:
    return _get_studio().export(project_id, Path(out_dir))


def get_project_status(project_id: str) -> dict:
    return _get_studio().get_status(project_id)


def regenerate_stage(project_id: str, stage: str) -> str | Path:
    return _get_studio().regenerate_stage(project_id, stage)


def record_review(project_id: str, stage: str, verdict: str, comment: str | None = None) -> None:
    _get_studio().record_review(project_id, stage, verdict, comment=comment)


def import_asset(project_id: str, capability: str, file_path: str) -> str:
    return _get_studio().import_asset(project_id, capability, file_path)
