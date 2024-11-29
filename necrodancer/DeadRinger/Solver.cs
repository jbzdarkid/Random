namespace DeadRinger;

public class State {
    public int beat;
    public int playerX;
    public int playerY;
    public int playerPreviousX;
    public int playerPreviousY;

    private List<Enemy> enemies = [];
    private List<Bell> bells = [];

    public void SetEnemies(List<Enemy> enemies) {
        this.enemies.Clear();
        foreach (Enemy enemy in enemies) {
            if (enemy is Bell bell) {
                this.bells.Add(bell.Clone());
            } else {
                this.enemies.Add(enemy.Clone());
            }
        }
    }

    public void GetEnemies(ref List<Enemy> enemies) {
        enemies.RemoveAll(e => e is not Bell); // Remove all non-bell entites
        enemies.RemoveRange(this.bells.Count, enemies.Count - this.bells.Count); // truncate list down to size
        while (enemies.Count < this.bells.Count) enemies.Add(new Bell(0, 0, null)); // uh

        // Copy state data 
        for (int i = 0; i < enemies.Count; i++) {
            if (this.bells[i].x != enemies[i].x && this.bells[i].y != enemies[i].y) System.Diagnostics.Debugger.Break();
            this.bells[i].CopyTo((Bell)enemies[i]);
        }

        foreach (Enemy enemy in this.enemies) enemies.Add(enemy.Clone());
    }
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

        Stack<State> stack = new();
        stack.Push(this.level.GetState());
        do {
            State state = stack.Pop();
            this.level.SetState(state);

            if (this.level.Won()) {
                this.solutions.Add(new(this.solution));
                Console.WriteLine("Found solution: ", string.Join(", ", this.solution));
                continue;
            }

            if (stack.Count >= 10)

            // if (this.solution.Count >= 15) continue; // uh what now

            this.level.SetState(state);
            foreach (Direction dir in toTry) {
                this.level.Move(dir);
                stack.Push(this.level.GetState());
            }

        } while (stack.Count > 0);

        return this.solutions;
    }

    private static Direction[] toTry = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.None];

    private void DFSStateGraph() {

    }
}
