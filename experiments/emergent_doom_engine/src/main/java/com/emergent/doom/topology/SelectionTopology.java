package com.emergent.doom.topology;

import com.emergent.doom.cell.Algotype;
import com.emergent.doom.cell.Cell;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Selection topology: Ideal target position per Levin paper.
 * Stub: Returns leftmost position (0); future: calculate sorted position.
 */
public class SelectionTopology<T extends Cell<T>> implements Topology<T> {
    @Override
    public List<Integer> getNeighbors(int position, int arraySize, Algotype algotype) {
        // Stub: Return leftmost position (0) as ideal target
        // Future: Calculate leftmost position where cell's value belongs in sorted order
        return Arrays.asList(0);
    }

    @Override
    public List<Integer> getIterationOrder(int arraySize) {
        return IntStream.range(0, arraySize).boxed().collect(Collectors.toList());
    }
}