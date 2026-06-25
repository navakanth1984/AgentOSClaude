from dataclasses import replace

from permission import mint_token, verify_token, PermissionToken

KEY = b"test-key"


def test_minted_token_verifies():
    tok = mint_token(KEY, classification="transfer", confidence=0.91, current_turn=3)
    assert verify_token(KEY, tok, current_turn=3) is True


def test_tampered_token_rejected():
    tok = mint_token(KEY, classification="transfer", confidence=0.91, current_turn=3)
    forged = replace(tok, confidence=0.10)
    assert verify_token(KEY, forged, current_turn=3) is False


def test_wrong_key_rejected():
    tok = mint_token(KEY, classification="transfer", confidence=0.91, current_turn=3)
    assert verify_token(b"other-key", tok, current_turn=3) is False


def test_expired_token_rejected():
    tok = mint_token(KEY, classification="transfer", confidence=0.91, current_turn=3, ttl_turns=0)
    assert verify_token(KEY, tok, current_turn=4) is False


def test_none_token_rejected():
    assert verify_token(KEY, None, current_turn=0) is False
