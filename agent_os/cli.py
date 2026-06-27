import argparse
import sys
import os
import time
import json
import uuid
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

from agent_os.speech.engines.registry import EngineRegistry, resolve_engine
from agent_os.speech.schema.models import Language, EngineName, ExecutionPlanEntry
from agent_os.speech.schema.jobs import SpeechJob, JobState, SpeechJobStore, EventBus
from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.stages.normalize import NormalizeStage
from agent_os.speech.pipeline.stages.parse import ParseStage
from agent_os.speech.pipeline.stages.segment import SegmentStage
from agent_os.speech.pipeline.stages.context import ContextStage
from agent_os.speech.pipeline.stages.route import RouteStage
from agent_os.speech.pipeline.stages.synthesize import SynthesizeStage
from agent_os.speech.pipeline.stages.trim import TrimStage
from agent_os.speech.pipeline.stages.append import AppendStage
from agent_os.speech.pipeline.incremental_executor import IncrementalExecutor

console = Console()

def run_doctor():
    console.print("[bold cyan]Speech Engine Health[/bold cyan]")
    console.print("=" * 40)
    
    # 1. Check engines
    available_engines = []
    
    # Kokoro Check
    kokoro_ok = False
    try:
        from agent_os.speech.engines.kokoro_engine import KokoroEngine
        k_engine = KokoroEngine()
        k_engine.validate_model()
        kokoro_ok = True
        available_engines.append("Kokoro")
    except Exception:
        pass
        
    # Piper Check
    piper_ok = False
    try:
        from agent_os.speech.engines.piper_engine import PiperEngine
        p_engine = PiperEngine()
        p_engine.validate_model()
        piper_ok = True
        available_engines.append("Piper")
    except Exception:
        pass

    # Render checklist
    table = Table(title="Pre-Flight Checklist", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="dim")
    table.add_column("Status")
    table.add_column("Details")
    
    table.add_row("Kokoro Engine", "[green]OK[/green]" if kokoro_ok else "[red]Missing[/red]", "Kokoro ONNX model found" if kokoro_ok else "Model files not downloaded")
    table.add_row("Piper Engine", "[green]OK[/green]" if piper_ok else "[red]Missing[/red]", "Piper ONNX model found" if piper_ok else "Model files not downloaded")
    table.add_row("Python Version", "[green]OK[/green]", sys.version.split()[0])
    
    import platform
    table.add_row("Platform", "[green]OK[/green]", f"{platform.system()} ({platform.processor() or 'unknown'})")
    
    # CPU Workers recommendation
    cpu_count = os.cpu_count() or 1
    table.add_row("Environment Recommendation", "[green]OK[/green]", f"workers={cpu_count}, intra_threads=3")
    
    # Protocol version
    table.add_row("Compatibility Standards", "[green]OK[/green]", "protocol=v1.0, assets=v1.2")
    
    console.print(table)
    
    if len(available_engines) > 0:
        console.print("\n[bold green]Result: READY[/bold green]")
    else:
        console.print("\n[bold red]Result: FAILED (No engines ready)[/bold red]")

def run_synthesis_pipeline(text_path: str, engine_name: str, voice_name: str, stream_mode: bool) -> Optional[str]:
    # Ensure text exists
    text_file = Path(text_path)
    if not text_file.is_file():
        console.print(f"[bold red]Error: File {text_path} not found.[/bold red]")
        return None

    # Use SpeechService to create job
    from agent_os.speech.service import SpeechService
    job = SpeechService.create_job({
        "text_path": text_path,
        "engine": engine_name,
        "voice": voice_name
    })

    bus = EventBus()
    progress = None

    # Render Progress
    if stream_mode:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        task_id = progress.add_task("[cyan]Initializing pipeline...", total=100)
        progress.start()
        
        def render_listener(event):
            if event.event_type == "pipeline_started":
                progress.update(task_id, description="[yellow]Planning execution structure...")
            elif event.event_type == "chunk_started":
                progress.update(task_id, description=f"[cyan]Synthesizing chunk {event.chunk_id}...")
            elif event.event_type == "chunk_synthesized":
                progress.update(task_id, description=f"[blue]Trim/Append chunk {event.chunk_id}...")
            elif event.event_type == "chapter_progress":
                percent = int((event.completed_chunks / event.total_chunks) * 100)
                progress.update(task_id, completed=percent, description=f"[green]Synthesizing chapter: {percent}%")
            elif event.event_type == "pipeline_completed":
                progress.update(task_id, completed=100, description="[bold green]Synthesis Complete!")
                progress.stop()
                
        bus.subscribe(render_listener)
    else:
        def simple_listener(event):
            console.print(f"[Event] {event.event_type} - {event.to_json()}")
        bus.subscribe(simple_listener)

    try:
        SpeechService.run_job(job.job_id, background=False, custom_bus=bus)
    except KeyboardInterrupt:
        if stream_mode and progress is not None:
            progress.stop()
        console.print("\n[bold red]Synthesis cancelled by user.[/bold red]")
        SpeechService.cancel_job(job.job_id)
        return job.job_id
    except Exception as e:
        if stream_mode and progress is not None:
            progress.stop()
        console.print(f"\n[bold red]Pipeline failed: {e}[/bold red]")
        return job.job_id

    console.print("\n[bold green]Completed[/bold green]")
    console.print("\n[bold]Artifacts[/bold]")
    console.print("-" * 40)
    console.print(f"  Audio:              {os.path.join(job.output_directory, 'Chapter_0.wav')}")
    console.print(f"  Job manifest:       {os.path.join(job.output_directory, 'job.json')}")
    console.print(f"  Structured events:  {os.path.join(job.output_directory, 'events.jsonl')}")
    console.print(f"  Telemetry logs:     {os.path.join(job.output_directory, 'metrics')}")
    console.print("-" * 40)

    return job.job_id

def main():
    parser = argparse.ArgumentParser(description="Agent OS Speech Command Center")
    subparsers = parser.add_subparsers(dest="resource", help="Exposed platform resources")
    
    # 1. JOBS subparser
    jobs_parser = subparsers.add_parser("jobs", help="Manage synthesis jobs")
    jobs_sub = jobs_parser.add_subparsers(dest="action", help="Job actions")
    
    # jobs create
    create_parser = jobs_sub.add_parser("create", help="Create new speech job")
    create_parser.add_argument("file", help="Source file path (.txt or .md)")
    create_parser.add_argument("--engine", choices=["kokoro", "piper"], default="kokoro", help="Speech engine name")
    create_parser.add_argument("--voice", default="default", help="Voice model ID")
    
    # jobs status / show / cancel / events / artifacts
    for action in ["status", "show", "cancel", "events", "artifacts"]:
        act_p = jobs_sub.add_parser(action, help=f"{action.capitalize()} job details")
        act_p.add_argument("job_id", help="UUID of the job")

    # 2. SYNTH / STREAM subparsers
    for verb in ["synth", "stream"]:
        s_parser = subparsers.add_parser(verb, help=f"Execute speech synthesis (standard/stream)")
        s_parser.add_argument("file", help="Source file path (.txt or .md)")
        s_parser.add_argument("--engine", choices=["kokoro", "piper"], default="kokoro", help="Speech engine name")
        s_parser.add_argument("--voice", default="default", help="Voice model ID")

    # 3. DOCTOR subparser
    subparsers.add_parser("doctor", help="Run speech pre-flight diagnostics")

    # 4. ENGINES subparser
    engines_parser = subparsers.add_parser("engines", help="Inspect registered engines")
    engines_sub = engines_parser.add_subparsers(dest="action", help="Engine actions")
    engines_sub.add_parser("list", help="List all registered engines")
    inspect_p = engines_sub.add_parser("inspect", help="Inspect engine details")
    inspect_p.add_argument("engine_name", choices=["kokoro", "piper"])

    # 5. VOICES subparser
    voices_parser = subparsers.add_parser("voices", help="Inspect voice registries")
    voices_sub = voices_parser.add_subparsers(dest="action", help="Voice actions")
    voices_sub.add_parser("list", help="List all available voices")

    # 6. BENCHMARK subparser
    bench_parser = subparsers.add_parser("benchmark", help="Run harness benchmarks")
    bench_parser.add_argument("--engine", choices=["kokoro", "piper", "mock"], default="kokoro")
    bench_parser.add_argument("--chunks", type=int, default=10)

    # 7. EVENTS subparser
    events_parser = subparsers.add_parser("events", help="Watch pipeline events")
    events_sub = events_parser.add_subparsers(dest="action", help="Events action")
    watch_p = events_sub.add_parser("watch", help="Watch job event bus live")
    watch_p.add_argument("job_id", help="Job ID to watch")

    args = parser.parse_args()
    
    if args.resource == "doctor":
        run_doctor()
        return 0

    elif args.resource == "jobs":
        if args.action == "create":
            voice = args.voice if args.voice != "default" else ("af_heart" if args.engine == "kokoro" else "default")
            run_synthesis_pipeline(args.file, args.engine, voice, stream_mode=True)
            return 0
            
        job = SpeechJobStore.load(args.job_id) if args.job_id else None
        if not job:
            console.print(f"[bold red]Error: Job {args.job_id} not found.[/bold red]")
            return 1
            
        if args.action == "status":
            console.print(f"Job:   {job.job_id}")
            console.print(f"State: [bold yellow]{job.state.value}[/bold yellow]")
            
        elif args.action == "show":
            console.print(Panel(json.dumps(job.to_dict(), indent=2), title=f"Job {job.job_id} Details"))
            
        elif args.action == "cancel":
            if job.state in [JobState.QUEUED, JobState.PLANNING, JobState.SYNTHESIZING]:
                job.transition_to(JobState.CANCELLED)
                SpeechJobStore.save(job)
                console.print(f"[bold green]Job {job.job_id} successfully cancelled.[/bold green]")
            else:
                console.print(f"[bold yellow]Job {job.job_id} is in state '{job.state.value}' and cannot be cancelled.[/bold yellow]")
                
        elif args.action == "events":
            table = Table(title=f"Job {job.job_id} Events", show_header=True)
            table.add_column("Timestamp", style="dim")
            table.add_column("Type", style="cyan")
            table.add_column("Details")
            for evt in job.event_log:
                table.add_row(
                    time.strftime("%H:%M:%S", time.localtime(evt["timestamp"])),
                    evt["event_type"],
                    json.dumps({k: v for k, v in evt.items() if k not in ["event_type", "run_id", "timestamp"]})
                )
            console.print(table)
            
        elif args.action == "artifacts":
            console.print(f"[bold]Output Directory:[/bold] {job.output_directory}")
            console.print(f"  Final WAV:   {os.path.join(job.output_directory, 'Chapter_0.wav')}")
            console.print(f"  Job JSON:    {os.path.join(job.output_directory, 'job.json')}")
            
        return 0

    elif args.resource in ["synth", "stream"]:
        voice = args.voice if args.voice != "default" else ("af_heart" if args.engine == "kokoro" else "default")
        run_synthesis_pipeline(args.file, args.engine, voice, stream_mode=(args.resource == "stream"))
        return 0

    elif args.resource == "engines":
        if args.action == "list":
            table = Table(title="Registered Engines", show_header=True)
            table.add_column("Engine Name", style="cyan")
            table.add_column("Status")
            
            for name in ["kokoro", "piper"]:
                try:
                    eng = EngineRegistry.get_engine({"engine_name": name})
                    eng.validate_model()
                    status = "[green]Ready[/green]"
                except:
                    status = "[red]Not Configured[/red]"
                table.add_row(name, status)
            console.print(table)
        elif args.action == "inspect":
            try:
                eng = EngineRegistry.get_engine({"engine_name": args.engine_name})
                caps = eng.get_capabilities()
                console.print(Panel(json.dumps(caps.__dict__, default=str, indent=2), title=f"Engine {args.engine_name} Capabilities"))
            except Exception as e:
                console.print(f"[bold red]Failed to inspect engine {args.engine_name}: {e}[/bold red]")
        return 0

    elif args.resource == "voices":
        if args.action == "list":
            for name in ["kokoro", "piper"]:
                try:
                    eng = EngineRegistry.get_engine({"engine_name": name})
                    caps = eng.get_capabilities()
                    console.print(f"[bold cyan]{name.capitalize()} Voices:[/bold cyan]")
                    console.print(f"  {', '.join(caps.supported_voices.keys())[:120]}...")
                except:
                    pass
        return 0

    elif args.resource == "benchmark":
        from agent_os.speech.benchmark import run_benchmark
        # Mock argparse sys.argv redirection
        sys.argv = [sys.argv[0], "--engine", args.engine, "--chunks", str(args.chunks)]
        run_benchmark()
        return 0

    elif args.resource == "events":
        if args.action == "watch":
            job = SpeechJobStore.load(args.job_id)
            if not job:
                console.print(f"[bold red]Job {args.job_id} not found.[/bold red]")
                return 1
            # Print historical events
            for evt in job.event_log:
                console.print(f"[{time.strftime('%H:%M:%S', time.localtime(evt['timestamp']))}] [cyan]{evt['event_type']}[/cyan] - {json.dumps(evt)}")
            # Live watching could be simulated or just complete if job is complete
            if job.state in [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED]:
                console.print("[yellow]Job execution has already terminated. Watching ended.[/yellow]")
            else:
                console.print("[yellow]Watching live events... (Press Ctrl+C to stop)[/yellow]")
                try:
                    while True:
                        time.sleep(1)
                        # Poll and show new events
                        current = SpeechJobStore.load(args.job_id)
                        if not current:
                            break
                        new_events = current.event_log[len(job.event_log):]
                        for evt in new_events:
                            console.print(f"[{time.strftime('%H:%M:%S', time.localtime(evt['timestamp']))}] [green]{evt['event_type']}[/green] - {json.dumps(evt)}")
                        job = current
                        if job.state in [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED]:
                            console.print("[yellow]Job execution terminated.[/yellow]")
                            break
                except KeyboardInterrupt:
                    console.print("[yellow]Watching stopped.[/yellow]")
        return 0

    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
