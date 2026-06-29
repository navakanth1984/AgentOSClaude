def synthesize(text: str, voice_name: str, speed: float = 1.0, lang: str = "en-IN") -> tuple:
    """DEPRECATED stub. Sarvam TTS now lives in the V1.1 pipeline.

    Use agent_os.speech.engines.sarvam_engine.SarvamEngine (returns (sample_rate,
    int16 ndarray)) or `python -m agent_os.cli audiobook <input> --engine sarvam`.
    """
    raise NotImplementedError(
        "Legacy tts.sarvam is retired. Use agent_os.speech.engines.sarvam_engine.SarvamEngine "
        "or the `cli audiobook --engine sarvam` path."
    )
