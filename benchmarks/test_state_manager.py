
import pytest
from cognitive_kernel.state import StateManager
from cognitive_kernel.transactions import TransactionManager
from cognitive_kernel.ontology import Goal

@pytest.fixture
def state_manager():
    """Provides a StateManager instance for benchmarking."""
    return StateManager()

@pytest.fixture
def transaction_manager():
    """Provides a TransactionManager instance."""
    return TransactionManager()

def test_commit_single_object(benchmark, state_manager, transaction_manager):
    """Benchmark committing a transaction with a single new object."""
    
    def setup():
        tx = transaction_manager.create_transaction()
        goal = Goal(description="Test goal", provenance=tx.transaction_id)
        tx.add(goal)
        return (state_manager, tx), {}

    def run(state_manager, tx):
        state_manager.commit(tx)

    benchmark.pedantic(run, setup=setup, rounds=100, iterations=10)

def test_commit_many_objects(benchmark, state_manager, transaction_manager):
    """Benchmark committing a transaction with many new objects."""
    num_objects = 100

    def setup():
        tx = transaction_manager.create_transaction()
        for i in range(num_objects):
            goal = Goal(description=f"Test goal {i}", provenance=tx.transaction_id)
            tx.add(goal)
        return (state_manager, tx), {}

    def run(state_manager, tx):
        state_manager.commit(tx)

    benchmark.pedantic(run, setup=setup, rounds=50, iterations=5)

def test_commit_with_dependencies(benchmark, state_manager, transaction_manager):
    """Benchmark committing a transaction with inter-object dependencies."""
    num_objects = 50

    def setup():
        # Pre-populate the state with some objects to depend on
        initial_tx = transaction_manager.create_transaction()
        dep_ids = []
        for i in range(num_objects):
            fact = Goal(description=f"Initial fact {i}", provenance=initial_tx.transaction_id)
            initial_tx.add(fact)
            dep_ids.append(fact.uuid)
        state_manager.commit(initial_tx)

        # The transaction to benchmark
        tx = transaction_manager.create_transaction()
        for i in range(num_objects):
            goal = Goal(
                description=f"Test goal {i}", 
                provenance=tx.transaction_id,
                dependencies=dep_ids[:i+1] # Add increasing number of dependencies
            )
            tx.add(goal)
        
        return (state_manager, tx), {}

    def run(state_manager, tx):
        state_manager.commit(tx)

    benchmark.pedantic(run, setup=setup, rounds=20, iterations=3)
