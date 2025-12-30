package com.emergent.doom.topology;

import com.emergent.doom.cell.Algotype;
import com.emergent.doom.cell.Cell;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Levin-paper topology: Dispatches neighbors based on algotype.
 * Faithful to cell-view behaviors (local/prefix/target).
 */
public class LevinTopology<T extends Cell<T>> implements Topology<T> {
    @Override
    public List<Integer> getNeighbors(int position, int arraySize, Algotype algotype) {
        switch (algotype) {
            case BUBBLE:
                // Levin p.8: left/right neighbors
                return getAdjacentNeighbors(position, arraySize);
            case INSERTION:
                // Levin p.8: all left cells (0 to position-1)
                return getLeftPrefixNeighbors(position);
            case SELECTION:
                // Levin p.8: ideal target (stub: 0; future: dynamic)
                return Arrays.asList(getIdealPosition(position));
            default:
                throw new IllegalArgumentException("Unknown algotype: " + algotype);
        }
    }

    private List<Integer> getAdjacentNeighbors(int position, int arraySize) {
        List<Integer> neighbors = new ArrayList<>();
        if (position > 0) neighbors.add(position - 1);
        if (position < arraySize - 1) neighbors.add(position + 1);
        return neighbors;
    }

    private List<Integer> getLeftPrefixNeighbors(int position) {
        return IntStream.range(0, position).boxed().collect(Collectors.toList());
    }

    // Stub: Levin Selection starts at leftmost (0); updates on block (Phase 2)
    private int getIdealPosition(int position) {
        return 0;
    }

    @Override
    public List<Integer> getIterationOrder(int arraySize) {
        // Sequential 0 to arraySize-1 (unchanged from Levin)
        return IntStream.range(0, arraySize).boxed().collect(Collectors.toList());
    }
}