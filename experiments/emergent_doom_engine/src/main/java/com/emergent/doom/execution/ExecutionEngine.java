package com.emergent.doom.execution;

import com.emergent.doom.cell.Cell;
import com.emergent.doom.probe.Probe;
import com.emergent.doom.swap.SwapEngine;
import com.emergent.doom.topology.Topology;

import java.util.List;

/**
 * Main execution engine that orchestrates cell dynamics.
 * 
 * <p>The ExecutionEngine is the heart of the EDE system, coordinating:
 * <ul>
 *   <li>Cell array management</li>
 *   <li>Swap attempts based on topology</li>
 *   <li>Probe recording</li>
 *   <li>Convergence detection</li>
 *   <li>Step-by-step iteration</li>
 * </ul>
 * </p>
 * 
 * @param <T> the type of cell
 */
public class ExecutionEngine<T extends Cell<T>> {
    
    private final T[] cells;
    private final Topology<T> topology;
    private final SwapEngine<T> swapEngine;
    private final Probe<T> probe;
    private final ConvergenceDetector<T> convergenceDetector;
    
    private int currentStep;
    private boolean converged;
    
    /**
     * IMPLEMENTED: Initialize the execution engine
     */
    public ExecutionEngine(
            T[] cells,
            Topology<T> topology,
            SwapEngine<T> swapEngine,
            Probe<T> probe,
            ConvergenceDetector<T> convergenceDetector) {
        this.cells = cells;
        this.topology = topology;
        this.swapEngine = swapEngine;
        this.probe = probe;
        this.convergenceDetector = convergenceDetector;
        this.currentStep = 0;
        this.converged = false;
        
        // Record initial state
        probe.recordSnapshot(0, cells, 0);
    }
    
    /**
     * IMPLEMENTED: Execute a single step of the algorithm
     * @return number of swaps performed in this step
     */
    public int step() {
        // Get iteration order from topology
        List<Integer> iterationOrder = topology.getIterationOrder(cells.length);
        
        // Reset swap counter for this step
        swapEngine.resetSwapCount();
        
        // For each cell in iteration order, try swapping with neighbors
        for (int i : iterationOrder) {
            List<Integer> neighbors = topology.getNeighbors(i, cells.length);
            for (int j : neighbors) {
                swapEngine.attemptSwap(cells, i, j);
            }
        }
        
        // Get swap count for this step
        int swaps = swapEngine.getSwapCount();
        
        // Increment step counter
        currentStep++;
        
        // Record snapshot
        probe.recordSnapshot(currentStep, cells, swaps);
        
        // Check convergence
        converged = convergenceDetector.hasConverged(probe, currentStep);
        
        return swaps;
    }
    
    /**
     * IMPLEMENTED: Run execution until convergence or max steps
     * @return total number of steps executed
     */
    public int runUntilConvergence(int maxSteps) {
        while (!converged && currentStep < maxSteps) {
            step();
        }
        return currentStep;
    }
    
    /**
     * IMPLEMENTED: Get the current cell array
     * Returns reference, not copy, for performance
     */
    public T[] getCells() {
        return cells;
    }
    
    /**
     * IMPLEMENTED: Get the current step number
     */
    public int getCurrentStep() {
        return currentStep;
    }
    
    /**
     * IMPLEMENTED: Check if execution has converged
     */
    public boolean hasConverged() {
        return converged;
    }
    
    /**
     * IMPLEMENTED: Get the probe for trajectory analysis
     */
    public Probe<T> getProbe() {
        return probe;
    }
    
    /**
     * IMPLEMENTED: Reset execution state to initial conditions
     */
    public void reset() {
        currentStep = 0;
        converged = false;
        probe.clear();
        swapEngine.resetSwapCount();
        topology.reset();
        convergenceDetector.reset();
        probe.recordSnapshot(0, cells, 0);
    }
}
