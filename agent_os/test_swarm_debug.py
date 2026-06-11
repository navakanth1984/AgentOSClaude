"""Debug: run swarm directly (no server) and print the full result."""
import sys, asyncio, json
sys.path.insert(0, ".")

from swarm import run_swarm

async def main():
    result = await run_swarm(
        "Obsidian knowledge management workflow",
        model="google/gemma-4-31b-it:free",
    )
    print("\n=== Swarm result ===")
    # Show error if any
    if "error" in result:
        print(f"TOP-LEVEL ERROR: {result['error']}")
    # Show individual agent results
    for r in result.get("results", []):
        status = "OK" if not r.get("error") else "ERR"
        print(f"  Agent #{r['agent_id']} [{r['role']}]: {status}")
        if r.get("error"):
            print(f"    error: {r['error']}")
        else:
            print(f"    result preview: {r['result'][:80]}")
    # Show summary
    print(f"\nsummary: successful={result.get('successful')}  notebooks={result.get('notebooks_found')}")
    print(f"note_path={result.get('note_path')}")

asyncio.run(main())
