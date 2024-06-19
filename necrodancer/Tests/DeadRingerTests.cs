using DeadRinger;
using System.Diagnostics;

namespace DeadRingerTest;

[TestClass]
public class DeadRingerTests {
    private Level level = Program.InitDeadRinger();

    [TestCleanup]
    public void Cleanup() {
        this.level.enemies.Clear();
    }

    private static Direction C2D(char c) => c switch {
        'N' => Direction.North,
        'E' => Direction.East,
        'S' => Direction.South,
        'W' => Direction.West,
        'X' => Direction.NorthSouth,
        'Y' => Direction.EastWest,
        _ => Direction.None,
    };

    private void SimulateAndTest(string test) {
        Debug.WriteLine($"Simulating test '{test}'");
        foreach (char c in test) {
            this.level.Move(C2D(c));
            if (Debugger.IsAttached) this.level.DrawGrid();
        }
    }

    [TestMethod]
    public void Oblivion() {
        string test = "ENNEEWWWWNWSWNNNEEENNENENNW";
        RNG.Seed([0]);
        this.SimulateAndTest(test);
    }
}
