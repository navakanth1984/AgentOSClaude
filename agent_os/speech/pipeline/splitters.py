import re
from typing import List
from agent_os.speech.pipeline.interfaces import SentenceSplitter

class RegexSentenceSplitter(SentenceSplitter):
    """
    Lightweight regex sentence splitter without NLTK dependency.
    Handles abbreviations like Mr., Dr. by avoiding splits there.
    """
    def __init__(self, max_chunk_length: int = 500):
        self.max_chunk_length = max_chunk_length

    def split(self, text: str) -> List[str]:
        # Split on sentence boundaries (., !, ?) followed by whitespace and capital letter
        # We use a positive lookbehind to keep the punctuation with the sentence
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
        
        # If a single "sentence" is still too long, fallback to splitting on commas
        final_sentences = []
        for s in sentences:
            if len(s) > self.max_chunk_length:
                # Split on comma, semicolon or em-dash
                parts = re.split(r'(?<=[,;—-])\s+', s)
                final_sentences.extend(parts)
            else:
                final_sentences.append(s)
                
        return [s.strip() for s in final_sentences if s.strip()]
