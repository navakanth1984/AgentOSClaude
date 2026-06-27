import re
import os
from agent_os.speech.pipeline.executor import StageContext

class NormalizeStage:
    # 1.2: explicit input contract — `input_path` (file) vs `input_text` (literal).
    # No longer probes input_text with os.path.exists, which silently read files
    # when prose happened to match a filename.
    version = "1.2"

    def _read_file(self, path: str) -> str:
        ext = os.path.splitext(path.lower())[1]
        if ext == ".pdf":
            try:
                import fitz  # PyMuPDF  # type: ignore  # optional dependency
                doc = fitz.open(path)
                return "\n".join(page.get_text() for page in doc)
            except Exception as e:
                raise RuntimeError(f"Failed to parse PDF {path}: {e}")
        elif ext == ".docx":
            try:
                import docx  # type: ignore  # optional dependency
                doc = docx.Document(path)
                return "\n".join(p.text for p in doc.paragraphs)
            except Exception as e:
                raise RuntimeError(f"Failed to parse DOCX {path}: {e}")
        else:
            # Text / Markdown / anything else: read as UTF-8.
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                raise RuntimeError(f"Failed to read file {path}: {e}")

    def run(self, context: StageContext, inputs: dict) -> dict:
        input_path = context.config.get("input_path")
        input_text = context.config.get("input_text")

        if input_path is not None and input_text is not None:
            raise ValueError(
                "NormalizeStage: provide exactly one of 'input_path' or 'input_text', not both."
            )

        if input_path is not None:
            if not os.path.isfile(input_path):
                raise FileNotFoundError(f"NormalizeStage: input_path not found: {input_path}")
            text = self._read_file(input_path)
        elif input_text is not None:
            # Always literal content — never interpreted as a path.
            text = input_text
        else:
            return {"normalized_text": ""}

        # Basic normalization:
        # 1. Replace smart quotes with straight quotes
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")

        # 2. Normalize horizontal whitespace (no multiple spaces/tabs)
        text = re.sub(r'[ \t]+', ' ', text)

        # 3. Ensure paragraphs are separated by exactly two newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return {"normalized_text": text.strip()}
