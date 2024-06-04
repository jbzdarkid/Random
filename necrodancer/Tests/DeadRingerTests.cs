using DeadRinger;
using System.Diagnostics;

namespace DeadRingerTest;

[TestClass]
public class DeadRingerTests {
    [TestCleanup]
    public void Cleanup() {
        Global.enemies.Clear();
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
            Player.Move(C2D(c));
            if (Player.x == 10) continue; // Still in the entryway, fight hasn't started yet.
            Global.SimulateBeat();
            if (Debugger.IsAttached) Program.DrawGrid();
        }
    }

    [TestMethod]
    public void Oblivion() {
        string test = "ENNEEWWWWNWSWNNNEEENNENENNW";
        RNG.Seed(0);
        Program.InitDeadRinger();
        this.SimulateAndTest(test);
    }

}
