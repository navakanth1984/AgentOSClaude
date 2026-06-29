import graphlib
from typing import Dict, Any, List, Set, Optional

class DAG:
    def __init__(self):
        self.nodes = {} # name -> Stage instance
        self.dependencies = {} # name -> set of dependent names

    def add_node(self, name: str, stage, depends_on: Optional[List[str]] = None):
        self.nodes[name] = stage
        self.dependencies[name] = set(depends_on or [])

    def get_execution_order(self) -> List[str]:
        sorter = graphlib.TopologicalSorter(self.dependencies)
        return list(sorter.static_order())
