from socratic import guard_turn, SocraticInterface
from knowledge import HouseplantKnowledgeProvider
from permission import mint_token

KEY = b"test-key"
BL = HouseplantKnowledgeProvider().leak_blocklist()


def test_guard_blocks_leak_while_locked():
    safe, blocked = guard_turn("It is overwatering and root rot.", token=None,
                               blocklist=BL, key=KEY, current_turn=1)
    assert blocked is True
    assert "overwatering" not in safe.lower()
    assert "root rot" not in safe.lower()


def test_guard_allows_clean_question_while_locked():
    safe, blocked = guard_turn("What might you test first, and why?", token=None,
                               blocklist=BL, key=KEY, current_turn=1)
    assert blocked is False
    assert safe == "What might you test first, and why?"


def test_guard_allows_answer_with_valid_token():
    tok = mint_token(KEY, classification="transfer", confidence=0.95, current_turn=1)
    safe, blocked = guard_turn("It is overwatering and root rot.", token=tok,
                               blocklist=BL, key=KEY, current_turn=1)
    assert blocked is False
    assert "root rot" in safe.lower()


def test_interface_uses_locked_prompt_and_guards_output():
    leaking_llm = lambda system, user: "The cause is overwatering and root rot."
    si = SocraticInterface(HouseplantKnowledgeProvider(), KEY, llm_fn=leaking_llm)
    text = si.respond({"turns": [{"role": "ai", "text": "hi", "turn_index": 0}]},
                      token=None, current_turn=1)
    assert "root rot" not in text.lower()


def test_interface_releases_answer_with_token():
    answering_llm = lambda system, user: "The cause is overwatering and root rot."
    si = SocraticInterface(HouseplantKnowledgeProvider(), KEY, llm_fn=answering_llm)
    tok = mint_token(KEY, classification="transfer", confidence=0.95, current_turn=1)
    text = si.respond({"turns": [{"role": "ai", "text": "hi", "turn_index": 0}]},
                      token=tok, current_turn=1)
    assert "root rot" in text.lower()
