"""
cinematic_controller.py — Cinematic OS: API Controller Layer

Translates HTTP request dicts into CinematicService calls, manages background
compilation runs via a decoupled JobService and BackgroundExecutor,
and formats outputs using stable response DTOs.
"""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from scene_manifest import CompileOptions, SceneManifest
from parser_protocol import ParserError
from cinematic_service import CinematicService
from natural_language_parser import NaturalLanguageParser
from cinematic_model_router import HybridGenerationRouter

# Import response DTOs
from api.response_models import CompileResponse, PresetResponse, ValidationResponse, JobStatusResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SceneManifestCodec — Decoupled parsing and reconstruction boundaries
# ---------------------------------------------------------------------------

class SceneManifestCodec:
    """Encapsulates all serialization and deserialization for SceneManifest."""

    @staticmethod
    def decode(payload: dict[str, Any]) -> SceneManifest:
        """Construct a validated SceneManifest object from raw dict."""
        return SceneManifest.from_dict(payload)

    @staticmethod
    def encode(manifest: SceneManifest) -> dict[str, Any]:
        """Convert a SceneManifest object back to a plain dictionary."""
        return manifest.to_dict()


# ---------------------------------------------------------------------------
# BackgroundExecutor Protocol & Implementations
# ---------------------------------------------------------------------------

@runtime_checkable
class BackgroundExecutor(Protocol):
    """Protocol for launching background tasks cleanly without blocking request threads."""

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> None:
        """Submit a callable to be run asynchronously in the background."""
        ...


class ThreadedBackgroundExecutor:
    """Simple executor that spawns a new daemon thread for background tasks."""

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> None:
        def _run_with_loop():
            import asyncio
            # Background thread needs its own running loop context for async tasks
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(fn(*args, **kwargs))
            finally:
                loop.close()

        thread = threading.Thread(target=_run_with_loop, daemon=True)
        thread.start()


class ImmediateBackgroundExecutor:
    """CI / Test executor that runs tasks synchronously in the same thread context."""

    def submit(self, fn: Any, *args: Any, **kwargs: Any) -> None:
        import asyncio
        try:
            # If a loop is already running in this thread, schedule it as a task
            loop = asyncio.get_running_loop()
            loop.create_task(fn(*args, **kwargs))
        except RuntimeError:
            # No running loop, run synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(fn(*args, **kwargs))
            finally:
                loop.close()


# ---------------------------------------------------------------------------
# JobService Protocol & Implementations
# ---------------------------------------------------------------------------

@runtime_checkable
class JobService(Protocol):
    """Protocol for managing job statuses for long-running compile pipelines."""

    def create_job(self, text: str, options: CompileOptions) -> str:
        ...

    def update_job(self, job_id: str, **kwargs: Any) -> None:
        ...

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        ...

    def list_jobs(self) -> list[dict[str, Any]]:
        ...


class InMemoryJobService:
    """Standard in-memory thread-safe implementation of JobService."""

    def __init__(self):
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_job(self, text: str, options: CompileOptions) -> str:
        job_id = f"job_cinematic_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "running",
                "stage": "parsing",
                "percent": 10,
                "text": text,
                "options": options,
                "result": None,
                "error": None,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "finished_at": None,
            }
        return job_id

    def update_job(self, job_id: str, **kwargs: Any) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(kwargs)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(j) for j in self._jobs.values()]


# ---------------------------------------------------------------------------
# CinematicAPI Protocol (public controller boundary)
# ---------------------------------------------------------------------------

@runtime_checkable
class CinematicAPI(Protocol):
    """Stable public interface contract for Cinematic API Controllers."""

    async def handle_compile(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        ...

    async def handle_generate_ir(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        ...

    async def handle_validate(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        ...

    async def handle_presets(self) -> tuple[int, dict[str, Any]]:
        ...

    async def handle_job_status(self, job_id: str) -> tuple[int, dict[str, Any]]:
        ...


# ---------------------------------------------------------------------------
# CinematicController
# ---------------------------------------------------------------------------

class CinematicController:
    """
    HTTP Controller for the Cinematic OS API.
    Provides transport-independent parsing, validation, and mapping.
    Satisfies the CinematicAPI Protocol contract.
    """

    def __init__(
        self,
        service: CinematicService | None = None,
        job_service_impl: JobService | None = None,
        executor: BackgroundExecutor | None = None,
    ):
        self._service = service or CinematicService()
        self._job_service = job_service_impl or InMemoryJobService()
        self._executor = executor or ThreadedBackgroundExecutor()

    async def handle_compile(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """
        POST /api/v1/cinematic/compile

        Compiles a raw SceneManifest directly to target prompts.
        """
        try:
            # Parse body options
            backend = body.get("backend", "flow_omni")
            multi_shot = bool(body.get("multi_shot", False))
            frame_rate = int(body.get("frame_rate", 24))
            options = CompileOptions(backend=backend, multi_shot=multi_shot, frame_rate=frame_rate)

            # Reconstruct SceneManifest using our codec
            manifest_raw = body.get("manifest")
            if not manifest_raw or not isinstance(manifest_raw, dict):
                return 400, {"error": "Missing or invalid 'manifest' field in request body"}

            try:
                manifest = SceneManifestCodec.decode(manifest_raw)
            except Exception as e:
                return 400, {"error": f"Failed to restore SceneManifest from dict: {e}"}

            # Direct sync compile
            result = await self._service.compile_from_manifest(manifest, options)
            if not result.succeeded:
                resp = CompileResponse.from_compile_result(result)
                resp["error"] = result.error or "Compilation failed"
                return 422, resp

            return 200, CompileResponse.from_compile_result(result)

        except Exception as e:
            logger.exception("Exception during cinematic compile")
            return 500, {"error": f"Internal controller error: {e}"}

    async def handle_generate_ir(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """
        POST /api/v1/cinematic/generate-ir

        Parses natural language text into SceneManifest and compiles to backends.
        Supports async parameter to run in background.
        """
        try:
            text = body.get("text", "").strip()
            if not text:
                return 400, {"error": "Missing or empty 'text' field in request body"}

            # Parse options
            backend = body.get("backend", "flow_omni")
            multi_shot = bool(body.get("multi_shot", False))
            frame_rate = int(body.get("frame_rate", 24))
            run_async = bool(body.get("async", False))
            options = CompileOptions(backend=backend, multi_shot=multi_shot, frame_rate=frame_rate)

            # Model selection context — passed through to parser → router → provider
            model_id = body.get("model", "").strip()
            provider_type = body.get("provider", "mock")  # "local" | "cloud" | "mock"
            routing_mode = body.get("routing_mode", "")
            parse_context: dict[str, Any] = {}

            if model_id and provider_type != "mock":
                # Build a real parser with the requested model wired in
                router = HybridGenerationRouter.from_env()
                if provider_type == "local":
                    parse_context["model_override"] = model_id
                elif provider_type == "gemini_direct":
                    parse_context["model"] = model_id
                else:
                    parse_context["model"] = model_id
                if routing_mode:
                    parse_context["routing_mode_override"] = routing_mode
                service = CinematicService(parser=NaturalLanguageParser(generation_router=router))
            else:
                service = self._service

            if run_async:
                # Spawn background task
                job_id = self._job_service.create_job(text, options)
                self._executor.submit(self._run_background_job, job_id, text, options, parse_context, service)
                return 202, {"job_id": job_id, "status": "running"}

            # Synchronous compilation
            result = await service.compile_from_text(text, options, context=parse_context if parse_context else None)
            if not result.succeeded:
                resp = CompileResponse.from_compile_result(result)
                resp["error"] = result.error or "Compilation failed"
                return 422, resp

            return 200, CompileResponse.from_compile_result(result)

        except ParserError as e:
            return 422, {"error": f"Parsing failed: {e}", "stage": e.stage, "raw_output": e.raw_output}
        except Exception as e:
            logger.exception("Exception during cinematic generate-ir")
            return 500, {"error": f"Internal controller error: {e}"}

    async def handle_validate(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        """
        POST /api/v1/cinematic/validate

        Performs three-stage validation of a SceneManifest without compiling.
        """
        manifest_raw = body.get("manifest")
        if not manifest_raw or not isinstance(manifest_raw, dict):
            return 400, {"error": "Missing or invalid 'manifest' field in request body"}

        try:
            manifest = SceneManifestCodec.decode(manifest_raw)
            errors = self._service.validate_manifest(manifest)
            return 200, ValidationResponse.from_errors(errors)
        except Exception as e:
            return 400, {"error": f"Invalid manifest structure: {e}"}

    async def handle_presets(self) -> tuple[int, dict[str, Any]]:
        """
        GET /api/v1/cinematic/presets

        Exposes stable, normalized camera, lighting, and style profiles.
        """
        # Encapsulated call - controller no longer reaches into compiler internals
        presets = self._service.get_presets()
        return 200, PresetResponse.from_raw_presets(presets)

    async def handle_job_status(self, job_id: str) -> tuple[int, dict[str, Any]]:
        """
        GET /api/v1/cinematic/job/{id}
        """
        job = self._job_service.get_job(job_id)
        if not job:
            return 404, {"error": f"Cinematic job with ID '{job_id}' not found"}

        # Serialize job status DTO
        return 200, JobStatusResponse.from_job_dict(job)

    # ------------------------------------------------------------------
    # Background execution worker
    # ------------------------------------------------------------------

    async def _run_background_job(
        self,
        job_id: str,
        text: str,
        options: CompileOptions,
        parse_context: dict[str, Any] | None = None,
        service: CinematicService | None = None,
    ) -> None:
        try:
            logger.info(f"Starting background cinematic job {job_id}")
            self._job_service.update_job(job_id, stage="parsing", percent=30)
            active_service = service or self._service
            result = await active_service.compile_from_text(text, options, context=parse_context)
            
            if result.succeeded:
                self._job_service.update_job(
                    job_id,
                    status="done",
                    stage="complete",
                    percent=100,
                    result=result,
                    finished_at=datetime.now(timezone.utc).isoformat(),
                )
                logger.info(f"Background cinematic job {job_id} succeeded")
            else:
                self._job_service.update_job(
                    job_id,
                    status="failed",
                    stage="failed",
                    percent=100,
                    error=result.error or "Unknown compilation error",
                    finished_at=datetime.now(timezone.utc).isoformat(),
                )
                logger.warning(f"Background cinematic job {job_id} failed: {result.error}")
        except Exception as e:
            self._job_service.update_job(
                job_id,
                status="failed",
                stage="failed",
                percent=100,
                error=f"Uncaught exception: {e}",
                finished_at=datetime.now(timezone.utc).isoformat(),
            )
            logger.exception(f"Background cinematic job {job_id} crashed")
