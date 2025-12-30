package com.emergent.doom.cell;

/**
 * Abstract base for Levin cell-view Selection Sort cells.
 * Baked-in: Algotype.SELECTION (target chasing, long-range).
 * Domain extends and impls compareTo.
 * TEMPLATE_BEGIN
 * PURPOSE: Provide Selection policy foundation (goal-directed).
 * INPUTS: value (int).
 * PROCESS:
 *   STEP[1]: Construct with value.
 *   STEP[2]: Return fixed SELECTION algotype.
 *   STEP[3]: Domain impls compareTo.
 * OUTPUTS: Cell<T> with SELECTION policy.
 * DEPENDENCIES: Cell interface; future internal idealPos state.
 * TEMPLATE_END
 */
public abstract class SelectionCell<T extends SelectionCell<T>> implements Cell<T> {
    protected final int value;

    protected SelectionCell(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    @Override
    public Algotype getAlgotype() {
        return Algotype.SELECTION;  // Baked-in
    }

    @Override
    public abstract int compareTo(T other);

    // Stub: Future Selection-specific (e.g., int getIdealPos();)
}