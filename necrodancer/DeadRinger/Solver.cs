using System.Collections;

namespace DeadRinger;

public class ShallowState {
    public int WinDistance;
    public ShallowState? n;
    public ShallowState? s;
    public ShallowState? e;
    public ShallowState? w;
    public ShallowState? x;
}

public class State {
    public ShallowState? Shallow;
    public State? n;
    public State? s;
    public State? e;
    public State? w;
    public State? x;
}

public class LinkedLoop<T> : IEnumerable<T> where T : class {
    public T? Previous => this.loopPointer?.Previous?.Value ?? this.list.Last?.Value;
    public T? Current => this.loopPointer?.Value;
    public int Count => this.list.Count;

    private LinkedList<T> list = new();
    private LinkedListNode<T>? loopPointer;

    public void AddCurrent(T node) {
        if (this.loopPointer == null) {
            this.loopPointer = this.list.AddFirst(node);
        } else {
            this.list.AddBefore(this.loopPointer, node);
            this.loopPointer = this.loopPointer.Previous;
        }
    }

    public void Advance() => this.loopPointer = this.loopPointer?.Next ?? this.list.First;

    public IEnumerator<T> GetEnumerator() => this.list.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => this.list.GetEnumerator();
}

public class Solver {
    private Level level;
    private HashSet<State> visitedNodes2 = new();
    public const int UNWINNABLE = int.MaxValue - 1;
    private int winningDepth = UNWINNABLE;

    LinkedList<State> unexplored = new();
    LinkedList<State> explored = new();

    LinkedLoop<ShallowState> explored2 = new();

    Stack<Direction> solution = new();
    List<Direction> bestSolution = new();

    public Solver(Level level) {
        this.level = level;
    }

    public int Score(State state) {
        int score = 0;
        // Count of bells rung?
        // Dead ringer stage (I guess implied with above)
        // Distance to exit

        return score;
    }

    List<Direction> Solve() {
        Console.WriteLine($"Solving {this.level.name}");
        State initialState = this.level.GetState();
        this.visitedNodes2.Add(initialState);

        initialState.Shallow = new ShallowState();
        this.unexplored.AddLast(initialState);

        this.BFSStateGraph();

        Console.WriteLine($"Traversal done in {this.visitedNodes2.Count} nodes.");

        this.ComputeWinningStates();

        int winningStates = 0;
        foreach (ShallowState shallow in this.explored2) {
            if (shallow.WinDistance != UNWINNABLE) winningStates++;
        }

        Console.WriteLine($"Of the {this.visitedNodes2.Count} nodes, {winningStates} are winning.");

        this.level.SetState(initialState); // Be polite and make sure we restore the original level state
        if (initialState.Shallow == null || initialState.Shallow.WinDistance == UNWINNABLE) {
            Console.WriteLine("Automatic solver could not find a solution.");
            int bestScore = 0;
            foreach (State state in this.explored) {
                int score = this.Score(state);
                if (score > bestScore) bestScore = score;
            }
            
            Console.WriteLine($"Best score: {bestScore}");
            foreach (State state in this.explored) {
                int score = this.Score(state);
                if (score == bestScore && state.Shallow != null) {
                    state.Shallow.WinDistance = 0;
                }
            }

            this.ComputeWinningStates();
        }

        Console.WriteLine($"Found the shortest # of moves: {initialState.Shallow?.WinDistance}");
        Console.WriteLine("Done computing victory states");

        this.DFSWinStates(initialState);

        return this.bestSolution;
    }

    void BFSStateGraph() {
        State depthMarker = new();
        depthMarker.Shallow = new ShallowState(); // Just so that state.Shallow.WinDistance is valid
        int depth = 0;
        this.unexplored.AddLast(depthMarker);

        while (this.unexplored.First?.Value != null) {
            State state = this.unexplored.First.Value;
            if (state.Shallow?.WinDistance == 0) { // Delayed addition of winning nodes to keep _explored in order
                this.unexplored.RemoveFirst();
                this.explored.AddLast(state);
                continue;
            }

            if (ReferenceEquals(state, depthMarker)) {
                Console.Write($"Finished processing depth {depth}, ");
                if (this.unexplored.Count == 1) { // Only the dummy state is left in queue, queue is essentially empty
                    Console.WriteLine("BFS exploration complete (no nodes remaining).");
                    break;
                } else if (this.visitedNodes2.Count > 150_000_000) {
                    Console.WriteLine("giving up (too many nodes).");
                    break;
                } else if (depth == this.winningDepth + 2) {
                    // I add a small fudge-factor here (2 iterations) to search for solutions
                    // which potentially take more moves, but have other advantages (like less damage, fewer items, etc)
                    Console.WriteLine($"not exploring any further, since the winning state was at depth {this.winningDepth}.");
                    break;
                }

                depth++;
                this.unexplored.RemoveFirst();
                Console.WriteLine($"there are {this.unexplored.Count} nodes to explore at depth {depth}");
                this.unexplored.AddLast(depthMarker);
                continue;
            }

            this.level.SetState(state);
            if (this.level.Move(Direction.North)) state.n = this.GetOrInsertState(depth);
            this.level.SetState(state);
            if (this.level.Move(Direction.South)) state.s = this.GetOrInsertState(depth);
            this.level.SetState(state);
            if (this.level.Move(Direction.East))  state.e = this.GetOrInsertState(depth);
            this.level.SetState(state);
            if (this.level.Move(Direction.West))  state.w = this.GetOrInsertState(depth);
            this.level.SetState(state);
            if (this.level.Move(Direction.None))  state.x = this.GetOrInsertState(depth);

            this.unexplored.RemoveFirst();
            this.explored.AddLast(state);
        }
    }

    State GetOrInsertState(int depth) {
        State state = this.level.GetState();
        bool inserted = this.visitedNodes2.Add(state);
        if (!inserted) return state; // State was already analyzed, or allocation failed

        if (this.visitedNodes2.Count % 100_000 == 0) {
            //_level->Print();
        }

        state.Shallow = new ShallowState();

        if (this.level.Won()) {
            state.Shallow.WinDistance = 0;
            if (this.winningDepth == UNWINNABLE) {
                // Once we find a winning state, we have reached the minimum depth for a solution.
                // Ergo, we should not explore the tree deeper than that solution. Since we're a BFS,
                // that means we should finish the current depth, but not explore any further.
                this.winningDepth = depth + 1; // +1 because the winning move is at the *next* depth, not the current one.
                Console.WriteLine($"Found the first winning state at depth {this.winningDepth}!");
            }
            // Even though this state is winning, we add it to the unexplored list as usual,
            // in order to keep the _explored list in depth-sorted order.
        }

        this.unexplored.AddLast(state);
        return state;
    }

    void CreateShallowStates() {
        this.explored2 = new LinkedLoop<ShallowState>(); // Clear the shallow state list in case we're re-evaluating after failing to win.

        // Second iteration because we need shallow copies of the udlr states. (maybe not?)
        Console.WriteLine("Populating shallow states:                                                                                                                                                    |");
        foreach (State state in this.explored) {
            ShallowState shallow = state.Shallow!;
            if (state.n != null) shallow.n = state.n.Shallow;
            if (state.s != null) shallow.s = state.s.Shallow;
            if (state.e != null) shallow.e = state.e.Shallow;
            if (state.w != null) shallow.w = state.w.Shallow;
            if (state.x != null) shallow.x = state.x.Shallow;
            this.explored2.AddCurrent(shallow);
            if (this.explored2.Count % (this.explored.Count / 100) == 0) Console.Write('#');
        }

        Console.WriteLine('|');
    }

    void ComputeWinningStates() {
        /* Even though we generate the list in order, we should not remove states from the loop, and we may need to do multiple loops.
                For example, consider this graph: A is at depth 0, B and D are at 1, C is at 2.
                A -> (D)
                    \v     ^\
                        B -> C

            Although C->D is a sub-optimal move (depth is decreasing), C is still a winning state. Since we process in depth order,
            we will process C, D, B, A -- ergo when we check D the first time it won't be marked winning.
            But, we do still want to mark C as winning -- since we haven't *truly* computed the costs yet, we don't know if it's faster.
        */

        // Reducing the memory required to represent the tree by removing sausages positions from State.
        // This helps to avoid paging with very large trees.
        this.CreateShallowStates();

        Console.WriteLine("Computing winning states to achieve the best score");

        // If (somehow) we make it through the entire loop and find no win states, this is the correct exit condition.
        // It is very likely that this value will be updated during iteration.
        ShallowState? endOfLoop = this.explored2.Previous;

        while (true) {
            ShallowState? shallow = this.explored2.Current;
            if (shallow == null) break; // All states are winning

            int winDistance = shallow.WinDistance;

            ShallowState? nextState = shallow.n;
            if (nextState != null && nextState.WinDistance < winDistance) winDistance = nextState.WinDistance;
            nextState = shallow.s;
            if (nextState != null && nextState.WinDistance < winDistance) winDistance = nextState.WinDistance;
            nextState = shallow.e;
            if (nextState != null && nextState.WinDistance < winDistance) winDistance = nextState.WinDistance;
            nextState = shallow.w;
            if (nextState != null && nextState.WinDistance < winDistance) winDistance = nextState.WinDistance;
            nextState = shallow.x;
            if (nextState != null && nextState.WinDistance < winDistance) winDistance = nextState.WinDistance;

            if (winDistance + 1 < shallow.WinDistance) {
                shallow.WinDistance = winDistance + 1;
                endOfLoop = this.explored2.Previous; // If we come back around without making any progress, stop.
            }

            if (shallow == endOfLoop) break; // We just processed the last node, and it wasn't winning.

            this.explored2.Advance();
        }
    }

    void DFSWinStates(State state) {
        // Recompute / readjust costs based on other penalties (e.g. damage taken, items used). TODO.
        /*
        if (state.Shallow?.WinDistance == 0) {
            if (totalMillis < _bestMillis
             || (totalMillis == _bestMillis && backwardsMovements > _bestBackwardsMovements)) {
                _bestSolution = _solution.Copy();
                _bestMillis = totalMillis;
                _bestBackwardsMovements = backwardsMovements;
            }
            return;
        }

        ComputePenaltyAndRecurse(state, state->u, Up, totalMillis, backwardsMovements);
        ComputePenaltyAndRecurse(state, state->d, Down, totalMillis, backwardsMovements);
        ComputePenaltyAndRecurse(state, state->l, Left, totalMillis, backwardsMovements);
        ComputePenaltyAndRecurse(state, state->r, Right, totalMillis, backwardsMovements);
        */
    }

    void ComputePenaltyAndRecurse(State state, State? nextState, Direction dir) {
        if (nextState?.Shallow == null) return; // Move would be illegal
        if (nextState.Shallow.WinDistance == UNWINNABLE) return; // Move is not ever winning
        if (state.Shallow!.WinDistance != nextState.Shallow.WinDistance + 1) return; // Move leads away from victory

        // Compute the duration of this motion

        /*
        // Speared state is not saved, because it's recoverable. Memory > speed tradeoff.
        // This is gross. It gets a little cleaner if I can use for-each, but not much.
        bool sausageSpeared = false;
        if (state->stephen.HasFork()) {
    #define o(x) +1
            for (u8 i=0; i<SAUSAGES; i++) {
    #undef o
                const Sausage& sausage = state->sausages[i];
                if (state->stephen.z != sausage.z) continue;
                if ((state->stephen.x == sausage.x1 && state->stephen.y == sausage.y1)
                    || (state->stephen.x == sausage.x2 && state->stephen.y == sausage.y2)) {
                    sausageSpeared = true;
                    break;
                }
            }
        }
        if (!sausageSpeared) {
            totalMillis += 160;

    #define o(x) if (state->sausages[x] != nextState->sausages[x]) totalMillis += 38;
            SAUSAGES;
    #undef o
        } else { // Movements are faster while spearing a sausage
            totalMillis += 158;

    #define o(x) if (state->sausages[x] != nextState->sausages[x]) totalMillis += 4;
            SAUSAGES;
    #undef o
        }

        if (WouldStephenStepOnGrill(state->stephen, dir)) totalMillis += 152; // TODO: Does this change while speared?
        // TODO: Does the sausage movement cost depend on your *current state* or the *next state*? I.e. if you unspear and roll a sausage behind you, do you pay for it?
        // TODO: Time sausage pushes as fork pushes (same latency as rotations?)
        // TODO: Time motion w/ sausage hat
        // TODO: Time motion w/ fork carry
        // TODO: Time motion as forkless -> rotations *and* lateral motion
        // TODO: Time motion when pushing a block
        // TODO: Ladder climbs while speared / non-speared?

        if (totalMillis > _bestMillis) return; // This solution is not faster than the known best path.

        if (state->stephen.dir == Up && dir == Down)                 backwardsMovements++;
        else if (state->stephen.dir == Down && dir == Up)        backwardsMovements++;
        else if (state->stephen.dir == Left && dir == Right) backwardsMovements++;
        else if (state->stephen.dir == Right && dir == Left) backwardsMovements++;
        */

        this.solution.Push(dir);
        this.DFSWinStates(nextState);
        this.solution.Pop();
    }

}
