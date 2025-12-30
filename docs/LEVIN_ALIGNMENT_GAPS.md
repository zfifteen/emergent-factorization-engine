# EDE-Levin Paper Alignment Gap Analysis

**Document Status**: CRITICAL - Implementation Divergences Identified
**Reference Paper**: Zhang, Goldstein, Levin (2024) "Classical Sorting Algorithms as a Model of Morphogenesis"
**Reference Path**: `docs/2401.05375v1.pdf`

---

## Executive Summary

The current Emergent Factorization Engine (EDE) has **fundamental architectural divergences** from the Levin paper methodology. These are not minor parameter differences but **core conceptual misalignments** that undermine the scientific validity of claiming Levin-style emergent dynamics.

**Severity**: SHOW-STOPPER
**Recommendation**: Refactor engine core before further development

---

## Divergence Inventory

### D1: CRITICAL - Algotype Definition Mismatch

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Definition** | Sorting algorithm controlling cell behavior | Energy function for scoring candidates |
| **Examples** | Bubble, Insertion, Selection | dirichlet5, arctan, zmetric |
| **Controls** | WHO cell can see and swap with | HOW energy value is calculated |
| **Biological analog** | Behavioral policy / "genetic identity" | N/A (optimization heuristic) |

**Paper Quote (p.6)**:
> "Each cell utilizes one of several sorting algorithms to dictate its movement. This 'Algotype' is constant for the life of the cell (i.e. roughly equivalent to a fixed genetic or phenotypic identity)."

**Current Code** (`heuristics/core.py`):
```python
# Algotypes are energy functions, NOT sorting algorithms
REGISTRY: Dict[str, EnergyFn] = {
    "dirichlet": dirichlet_energy,
    "arctan": arctan_geodesic_energy,
    ...
}
```

**Impact**: The entire meaning of "algotype" is wrong. The paper's chimeric experiments depend on cells following different SORTING RULES, not different energy calculations.

---

### D2: CRITICAL - Swap Partner Selection Logic

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Bubble Sort** | Swap with LEFT or RIGHT neighbor | Always adjacent only |
| **Insertion Sort** | View ALL cells to left, swap with LEFT neighbor | Always adjacent only |
| **Selection Sort** | Swap with cell at "ideal target position" (ANY position) | Always adjacent only |
| **Algorithm awareness** | Cell knows its algorithm and acts accordingly | Cell has no algorithm, only energy |

**Paper Quote (p.8)** - Cell-view Bubble Sort:
> "Each cell is able to view and swap with either its left or right neighbor."

**Paper Quote (p.8)** - Cell-view Selection Sort:
> "Each cell can view and swap with the cell that currently occupies its ideal position."

**Current Code** (`engine/engine.py:91-108`):
```python
# ALWAYS adjacent - no algorithm-specific swap logic
for i in idxs:
    a = self.cells[i]
    b = self.cells[i + 1]  # ALWAYS i+1, regardless of "algotype"
    if e_left > e_right:
        swap(a, b)
```

**Impact**: Selection sort's ability to reach any position is completely missing. The algorithms that exhibit different error tolerance and delayed gratification behaviors cannot emerge because they don't exist.

---

### D3: CRITICAL - Swap Decision Criterion

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Comparison basis** | Cell VALUE (integer for sorting position) | Cell ENERGY (heuristic score) |
| **Decision rule** | "value is smaller/bigger than neighbor's value" | "energy is higher than neighbor's energy" |
| **Goal** | Achieve monotonic VALUE ordering | Rank by lowest ENERGY |

**Paper Quote (p.8)** - Cell-view Bubble Sort:
> "Active cell moves to the left if its **value** is smaller than that of its left neighbor, or active cell moves to the right if its **value** is bigger than that of its right neighbor."

**Current Code** (`engine/engine.py:101-108`):
```python
e_left = self.energy_of(a)   # Energy, not value
e_right = self.energy_of(b)  # Energy, not value
if e_left > e_right:         # Energy comparison, not value
    swap(a, b)
```

**Impact**: The paper's model is about SORTING BY VALUE. The current engine is doing OPTIMIZATION BY ENERGY. These are fundamentally different operations with different emergent properties.

---

### D4: CRITICAL - Missing Sorting Algorithm Implementations

**Paper defines 3 cell-view algorithms (p.8)**:

1. **Cell-view Bubble Sort**
   - View/swap with left OR right neighbor
   - Move left if value < left neighbor
   - Move right if value > right neighbor

2. **Cell-view Insertion Sort**
   - View ALL cells to left
   - Swap only with left neighbor
   - Move left only if left side is sorted AND value < left neighbor

3. **Cell-view Selection Sort**
   - Has an "ideal target position" (starts at leftmost)
   - Can view/swap with cell at ideal position
   - Swap if own value < target position cell's value
   - Update ideal position on rejection

**Current Implementation**: NONE of these algorithms exist. There is only one swap rule based on energy comparison.

---

### D5: HIGH - Parallelism vs Sequential Execution

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Execution model** | Multi-threaded, parallel | Sequential sweep |
| **Cell activation** | "All cells have a chance to move at each time step" | One cell pair checked at a time |

**Paper Quote (p.8)**:
> "We used multi-thread programming to implement the cell-view sorting algorithms. 2 types of threads were involved... cell threads are used to represent all cells, with each cell represented by a single thread"

**Current Code** (`engine/engine.py:90-108`):
```python
# Sequential iteration, not parallel
for i in idxs:
    a = self.cells[i]
    b = self.cells[i + 1]
    # ... synchronous swap
```

**Impact**: The emergent behaviors in the paper arise from parallel, concurrent cell actions. Sequential execution may produce different dynamics.

---

### D6: HIGH - Cell Value vs Cell Purpose

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Cell value meaning** | Integer determining sort position | Integer candidate for factorization |
| **Value usage** | Compared to neighbors for swap decision | Used to compute energy |
| **Goal** | Arrange values in monotonic order | Find factor of N |

**Paper Quote (p.6)**:
> "Cell: Basic element to be sorted by the sorting algorithms. Each cell has an integer value property which is used for the comparison during the sorting process."

**Impact**: The paper's cells ARE the values being sorted. In EDE, cells HAVE values but sort by energy. This inverts the model.

---

### D7: MEDIUM - Sortedness Metric Inconsistency

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Definition** | Percentage in correct monotonic order by VALUE | Inversions counted by VALUE |
| **Relevance** | Directly measures sorting progress | Measures value ordering but swaps by energy |

**Current Code** (`metrics/core.py:9-17`):
```python
def sortedness(values: Sequence[int]) -> float:
    # Counts VALUE inversions correctly
    inversions = sum(1 for a, b in zip(values, values[1:]) if a > b)
    return 1.0 - inversions / (len(values) - 1)
```

**Issue**: The sortedness metric is correct per the paper, but it's measuring VALUE ordering while the engine swaps by ENERGY. This creates a disconnect - the engine isn't actually trying to improve sortedness.

---

### D8: MEDIUM - Chimeric Array Meaning

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Chimeric meaning** | Cells using different SORTING algorithms | Cells using different ENERGY functions |
| **Aggregation cause** | Different movement patterns from different algorithms | Different energy values from different functions |
| **Paper's finding** | Algorithms cluster together during sorting | N/A - no true algorithm mixing |

**Paper Quote (p.12-13)**:
> "A cell-view (local) implementation of sorting policies enables an experiment that is not done in traditional sorting: chimeric arrays in which individual cells follow their own distinct policies ('Algotype') for how to move"

**Impact**: The paper's aggregation findings depend on cells with different BEHAVIORAL POLICIES interacting. Energy function mixing is not equivalent.

---

### D9: MEDIUM - Frozen Cell Semantics

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **Type 1 (Movable)** | Cannot initiate swap, CAN be moved by others | Similar |
| **Type 2 (Immovable)** | Cannot move OR be moved | Similar |
| **Context** | Frozen cells can't execute their SORTING ALGORITHM | Frozen cells can't participate in ENERGY swaps |

**Current Code** (`engine/engine.py:94-99`):
```python
if self.type2_immovable and (a.frozen or b.frozen):
    continue
if a.frozen and b.frozen:
    continue
```

**Partial Match**: The frozen logic is similar but operates in a different context (energy swaps vs sorting algorithm execution).

---

### D10: LOW - Delayed Gratification Context

| Aspect | Levin Paper | Current EDE |
|--------|-------------|-------------|
| **DG definition** | Temporarily decrease SORTEDNESS to later improve it | Same definition |
| **DG mechanism** | Emerges from cells routing around frozen cells | Emerges from energy dynamics |
| **Measurement** | Peak-Valley-Higher Peak in sortedness | Same measurement |

**Current Code** (`metrics/core.py:40-123`): DG detection is implemented correctly per the paper's definition.

**Issue**: DG is correctly measured but emerges from the wrong dynamics. In the paper, DG comes from sorting around defects. In EDE, it comes from energy optimization.

---

## Conceptual Model Comparison

### Levin Paper Model

```
PURPOSE: Sort array of integers by VALUE
         (Morphogenesis analog - organs finding correct positions)

CELL: { value: int, algotype: BubbleSort|InsertionSort|SelectionSort, frozen: bool }

ALGOTYPE determines:
  - Who can I see? (neighbors only, all left, any position)
  - Who can I swap with? (neighbor, target position)
  - When do I swap? (my value vs their value comparison)

SWAP DECISION: Compare VALUES
  - Bubble: value < left_neighbor.value → move left
  - Selection: value < target_cell.value → swap to target

GOAL STATE: Array sorted by VALUE (monotonic increasing)

EMERGENT BEHAVIORS:
  - Delayed Gratification: Routing around frozen cells
  - Aggregation: Same-algorithm cells cluster during sorting
  - Error Tolerance: Distributed algorithms handle defects better
```

### Current EDE Model

```
PURPOSE: Rank candidates by ENERGY for factorization
         (Optimization problem - find lowest energy)

CELL: { n: int, algotype: str (energy function name), frozen: bool, energy: Decimal }

ALGOTYPE determines:
  - How to calculate energy for this cell's n value
  - (Does NOT affect swap behavior)

SWAP DECISION: Compare ENERGIES
  - Always: energy(left) > energy(right) → swap
  - No algorithm-specific rules

GOAL STATE: Array sorted by ENERGY (lowest first)

BEHAVIORS:
  - Some DG episodes from energy dynamics
  - Aggregation from energy function grouping
  - NOT the same as paper's emergent phenomena
```

---

## Summary of Required Changes

| Priority | Gap | Required Fix |
|----------|-----|--------------|
| P0 | D1 | Redefine algotype as sorting algorithm enum (Bubble, Insertion, Selection) |
| P0 | D2 | Implement algorithm-specific swap partner selection |
| P0 | D3 | Change swap decision to VALUE comparison, not energy |
| P0 | D4 | Implement all three cell-view sorting algorithms |
| P1 | D5 | Consider parallel execution model |
| P1 | D6 | Clarify cell value role - IS the sorting key |
| P1 | D7 | Sortedness should align with swap criterion |
| P2 | D8 | True chimeric = different algorithms, not energies |
| P2 | D9 | Frozen semantics in context of sorting |
| P3 | D10 | DG from correct mechanism |

---

## Questions for Resolution

1. **Purpose Reconciliation**: How do we reconcile Levin's "sort by value" with EDE's "rank by energy for factorization"? Are we building:
   - A faithful Levin replication (sort integers)
   - A Levin-inspired factorization engine (adapt principles)
   - Something else?

2. **Energy Role**: In a faithful implementation, where does "energy" fit? The paper doesn't use energy for swap decisions - cells compare VALUES.

3. **Factorization Application**: If we faithfully implement Levin sorting, how does that help factorization? The original paper is about morphogenesis, not number theory.

---

## Next Steps

1. **Decision Point**: Confirm project direction (faithful replication vs adaptation)
2. **Architecture Redesign**: If faithful replication, redesign Cell and Engine classes
3. **Algorithm Implementation**: Implement the three cell-view sorting algorithms
4. **Test Against Paper**: Reproduce paper's experiments (efficiency, error tolerance, DG, aggregation)
5. **Then Adapt**: Once faithful, explore how to apply to factorization

---

*Document created: Investigation of EDE vs Levin paper alignment*
*Status: Awaiting direction on resolution approach*
