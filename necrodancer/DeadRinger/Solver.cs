using System.Collections;

namespace DeadRinger;

public class State {
    public int beat;
    public int playerX;
    public int playerY;
    public int playerPreviousX;
    public int playerPreviousY;
    public List<Enemy> enemies = [];
}

public class Solver {
    private Level level;

    Stack<Direction> solution = new();
    List<List<Direction>> solutions = new();

    public Solver(Level level) {
        this.level = level;
    }

    public List<List<Direction>> Solve() {
        Console.WriteLine($"Solving {this.level.name}");
        this.DFSStateGraph();

        return this.solutions;
    }

    private static Direction[] toTry = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.None];

    private void DFSStateGraph() {
        if (this.level.Won()) {
            this.solutions.Add(new(this.solution));
            Console.WriteLine("Found solution: ", string.Join(", ", this.solution));
            return;
        }

        if (this.solution.Count >= 10) return;

        State state = this.level.GetState();
        foreach (Direction dir in toTry) {
            this.level.Move(dir);
            this.solution.Push(dir);
            this.DFSStateGraph();
            this.solution.Pop();
            this.level.SetState(state);
        }
    }
}
