package com.emergent.doom.topology;

import com.emergent.doom.cell.Algotype;
import com.emergent.doom.cell.Cell;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Insertion topology: Prefix left view per Levin paper.
 * Cells see all positions to the left (0 to position-1).
 */
public class InsertionTopology<T extends Cell<T>> implements Topology<T> {
    @Override
    public List<Integer> getNeighbors(int position, int arraySize, Algotype algotype) {
        return IntStream.range(0, position).boxed().collect(Collectors.toList());
    }

    @Override
    public List<Integer> getIterationOrder(int arraySize) {
        return IntStream.range(0, arraySize).boxed().collect(Collectors.toList());
    }
}