import json
from pathlib import Path
from typing import Dict

from agent_os.speech.schema.models import EngineCapabilities, VoiceMap, ParseResult

class VoiceManager:
    """
    Handles Voice Lookup, Speaker Mapping, Capability Negotiation,
    and Lockfile Management as specified in ADR-015.
    """
    
    @staticmethod
    def ensure_lockfile(project_dir: str, transcript: ParseResult, capabilities: EngineCapabilities) -> VoiceMap:
        lockfile_path = Path(project_dir) / "voice_map.json"
        
        if lockfile_path.exists():
            with open(lockfile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return VoiceMap(
                schema_version=data.get("schema_version", "1.0"),
                engine=data.get("engine", capabilities.engine_name),
                voices=data.get("voices", {})
            )
            
        print("voice_map.json not found. Generating VoiceManager lockfile...")
        
        voices = {}
        speakers = set()
        for segment in transcript.segments:
            speakers.add(segment.speaker)
            
        available_voices = list(capabilities.supported_voices.keys())
        if not available_voices:
            raise RuntimeError(f"Engine {capabilities.engine_name} reported no available voices.")

        voice_index = 0
        for speaker in sorted(list(speakers)):
            v = available_voices[voice_index % len(available_voices)]
            voices[speaker] = v
            voice_index += 1
            
        voice_map = VoiceMap(
            schema_version="1.0",
            engine=capabilities.engine_name,
            voices=voices
        )
        
        lockfile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lockfile_path, "w", encoding="utf-8") as f:
            json.dump({
                "schema_version": voice_map.schema_version,
                "engine": voice_map.engine,
                "voices": voice_map.voices
            }, f, indent=4)
            
        return voice_map

    @staticmethod
    def resolve_voice(speaker: str, voice_map: VoiceMap, capabilities: EngineCapabilities) -> str:
        """
        Resolves the appropriate voice for a speaker using the map and engine capabilities.
        Falls back safely if the mapped voice isn't supported.
        """
        requested_voice = voice_map.voices.get(speaker)
        available_voices = list(capabilities.supported_voices.keys())
        
        if requested_voice and requested_voice in capabilities.supported_voices:
            return requested_voice
            
        # Fallback
        if available_voices:
            return available_voices[0]
            
        raise RuntimeError(f"No voices available in engine capabilities for {capabilities.engine_name}")
