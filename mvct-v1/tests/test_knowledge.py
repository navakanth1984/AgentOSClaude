from knowledge import HouseplantKnowledgeProvider


def test_provider_supplies_scenario_and_answer():
    p = HouseplantKnowledgeProvider()
    assert "houseplant" in p.scenario_prompt().lower()
    assert len(p.canonical_answer()) > 0


def test_blocklist_includes_core_plant_variables():
    p = HouseplantKnowledgeProvider()
    bl = {b.lower() for b in p.leak_blocklist()}
    for term in ("water", "light", "soil", "drainage"):
        assert term in bl
