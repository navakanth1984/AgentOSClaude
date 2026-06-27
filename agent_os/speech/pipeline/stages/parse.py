from agent_os.speech.pipeline.executor import StageContext
from agent_os.speech.parsers.classifier import classify_document
from agent_os.speech.parsers.parsers import ScreenplayParser, NovelParser
from agent_os.speech.schema.models import ParsePolicy, ClassificationResult

class ParseStage:
    version = "1.0"
    
    def run(self, context: StageContext, inputs: dict) -> dict:
        # 1. Retrieve the artifact from the normalize stage
        normalize_artifact = inputs.get("normalize", {})
        text = normalize_artifact.get("normalized_text", "")
        
        if not text:
            return {"transcript": None, "parser_raw": "{}"}

        chapter_id = context.config.get("chapter_id", "0")

        # Benchmark path: deterministic offline parser, fully separate from the
        # production (Gemini) path. Selected by config, never a fallback.
        if context.config.get("parser") == "benchmark":
            from agent_os.speech.parsers.benchmark_parser import BenchmarkParser
            parse_result, raw_json = BenchmarkParser().parse(text, chapter_id=chapter_id)
            return {
                "transcript": parse_result,
                "parser_raw": raw_json,
                "classification": ClassificationResult(document_type="benchmark", confidence=1.0),
            }

        # 2. Source Classifier
        classification = classify_document(text)
        
        # 3. Parser Selection
        policy_str = context.config.get("parse_policy", "balanced")
        try:
            policy = ParsePolicy(policy_str)
        except ValueError:
            policy = ParsePolicy.BALANCED
            
        if classification.document_type == "screenplay" or (classification.document_type == "plain_text" and "INT." in text):
            parser = ScreenplayParser(policy=policy)
        else:
            # Default to NovelParser for novels and markdown
            parser = NovelParser(policy=policy)
            
        # 4. LLM Extraction and Schema Validation
        # The parser internal logic uses Pydantic schema validation to ensure types
        # and returns a highly structured ParseResult dataclass + the raw string.
        parse_result, raw_json = parser.parse(text, chapter_id=chapter_id)
        
        # We store both the validated structured data and the raw JSON.
        return {
            "transcript": parse_result,
            "parser_raw": raw_json,
            "classification": classification
        }
