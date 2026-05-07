import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.analyze import god_nodes, surprising_connections, suggest_questions

# Load extraction data
extraction_path = Path('graphify-out/.graphify_extract.json')
extraction = json.loads(extraction_path.read_text(encoding='utf-8'))

# Build graph
G = build_from_json(extraction)

# Compute analyses
god = god_nodes(G)
surprising = surprising_connections(G)[:10]  # top 10
questions = suggest_questions(G)[:10]          # top 10

# Output results as JSON for easy parsing
output = {
    "god_nodes": god,
    "surprising_connections": surprising,
    "suggested_questions": questions
}
print(json.dumps(output, indent=2))
