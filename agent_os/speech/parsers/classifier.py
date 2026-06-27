import re
from agent_os.speech.schema.models import ClassificationResult

def classify_document(text: str) -> ClassificationResult:
    """
    Heuristic classifier to determine document type.
    Treats the classifier as a confidence scorer, not a hard decision maker.
    """
    if not text:
        return ClassificationResult(document_type="plain_text", confidence=1.0)

    # Check for screenplay indicators
    screenplay_indicators = ["INT.", "EXT.", "CUT TO:", "FADE IN:", "FADE OUT:"]
    screenplay_matches = sum(1 for indicator in screenplay_indicators if indicator in text)
    
    # Check for novel indicators
    novel_indicators = [r"Chapter \d+", r"Part \d+"]
    novel_matches = sum(1 for indicator in novel_indicators if re.search(indicator, text, re.IGNORECASE))
    
    # Check for markdown indicators
    markdown_matches = len(re.findall(r'^#+ ', text, re.MULTILINE))
    
    if screenplay_matches > 0:
        confidence = min(0.6 + (screenplay_matches * 0.1), 0.95)
        return ClassificationResult(document_type="screenplay", confidence=confidence)
    
    if novel_matches > 0 or '"' in text or '“' in text:
        # Novels typically have heavy use of quotes for dialogue
        quote_count = text.count('"') + text.count('“')
        confidence = 0.5
        if novel_matches > 0:
            confidence += 0.2
        if quote_count > 10:
            confidence += 0.2
        return ClassificationResult(document_type="novel", confidence=min(confidence, 0.95))
        
    if markdown_matches > 0:
        confidence = min(0.6 + (markdown_matches * 0.1), 0.95)
        return ClassificationResult(document_type="markdown", confidence=confidence)
        
    return ClassificationResult(document_type="plain_text", confidence=0.8)
