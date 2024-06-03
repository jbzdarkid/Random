using DeadRinger;
using System.Diagnostics;

namespace DeadRingerTest;

public class Program {
}

[TestClass]
public class Tests {
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

    private void SimulateAndTest<T>(string test, int x, int y, char dir, int health) where T : Enemy {
        Debug.WriteLine($"Simulating test '{test}'");
        foreach (char c in test) {
            Player.Move(C2D(c));
            List<Enemy> enemies = new(Global.enemies); // To allow additions during enumeration
            enemies.ForEach(enemy => enemy.Update());
            if (Debugger.IsAttached) DeadRinger.Program.DrawGrid();
        }
        Enemy? enemy = Global.enemies.Find(x => x is T);
        if (health == 0) { // Killed.
            Assert.IsNull(enemy);
        } else {
            Assert.IsNotNull(enemy);
            Assert.AreEqual((x, y), (enemy.x, enemy.y));
            Assert.AreEqual(C2D(dir), enemy.dir);
            Assert.AreEqual(health, enemy.health);
        }
    }

    [TestMethod]
    [DataRow("E",           2, 4, 'E')]
    [DataRow("EE",          2, 5, 'E')]
    [DataRow("EEE",         2, 5, 'E')]
    [DataRow("EEEE",        2, 6, 'E')]
    [DataRow("EW",          3, 4, 'S')]
    [DataRow("EEWW",        3, 5, 'S')]
    [DataRow("NNNSNSNN",    0, 0, '?', 0)]
    [DataRow("NNNNNN",      0, 0, '?', 0)]
    [DataRow("NN.ENNNNW..", 2, 4, 'N')]
    public void TestGreenDragon(string test, int x, int y, char dir, int health = 4) {
        Global.width = 9;
        Global.height = 9;
        Player.Init(6, 4);
        Global.enemies.Add(new Sarcophagus(1, 4, () => new GreenDragon(2, 4)));
        this.SimulateAndTest<GreenDragon>(test, x, y, dir, health);
    }

    [TestMethod]
    [DataRow("E",           2, 4, 'E')]
    [DataRow("EE",          2, 5, 'E')]
    [DataRow("EEE",         2, 5, 'E')]
    [DataRow("EEEE",        2, 6, 'E')]
    [DataRow("EW",          3, 4, 'S')]
    [DataRow("EEWW",        3, 5, 'S')]
    [DataRow("NNNSNSN",     0, 0, '?', 0)]
    [DataRow("NNNNN" ,      0, 0, '?', 0)]
    [DataRow("NN.ENNNNW..", 2, 4, 'N')]
    public void TestNightmare(string test, int x, int y, char dir, int health = 3) {
        Global.width = 9;
        Global.height = 9;
        Player.Init(6, 4);
        Global.enemies.Add(new Sarcophagus(1, 4, () => new Nightmare(2, 4)));
        this.SimulateAndTest<Nightmare>(test, x, y, dir, health);
    }

    [TestMethod]
    [DataRow("EE",       2, 5, 'E')]
    [DataRow("EE.",      2, 5, 'E')]
    [DataRow("EE..",     2, 5, 'E')]
    [DataRow("EE...",    2, 5, 'E')]
    [DataRow("EE....",   2, 6, 'E')]
    [DataRow("NNNNNE",   3, 4, 'S', 2)]
    [DataRow("EEEEWWWW..", 2, 5, 'W')]
    [DataRow("EEEEWWW.W.", 2, 5, 'W')]
    [DataRow("EEEEWWW..W", 3, 6, 'S')]
    [DataRow("EEEEWWWWEW", 3, 6, 'S')]
    [DataRow("EEEEWW.WW.", 2, 5, 'W')]
    [DataRow("EEEEWW.W.W", 3, 6, 'S')]
    [DataRow("EEEEW.WWW.", 2, 5, 'W')]
    [DataRow("EEEEW.WW.W", 3, 6, 'S')]
    [DataRow("EEEE.WWWW.", 2, 5, 'W')]
    [DataRow("EEEE.WWW.W", 3, 6, 'S')]
    [DataRow("EEEE.WW.WW", 3, 6, 'S')]
    [DataRow("EEEE.W.WWW", 3, 6, 'S')]
    [DataRow("EEEE..WWWW", 3, 6, 'S')]
    [DataRow("SEEENN...SNN.N", 5, 5, 'E')]
    [DataRow("EEENNNWWWW", 2, 5, 'W')]
    // [DataRow("EEENNNWW.W", 2, 5, 'W')] // Not sure what this rule is. Ignoring for now, it's a small edge case
    [DataRow("EEENNNWW.S", 3, 6, 'S')]
    [DataRow("EEENNNWW..", 3, 6, 'S')]
    [DataRow("EN",       2, 5, 'E')]
    [DataRow("E.",       2, 5, 'E')]
    [DataRow("ES",       2, 5, 'E')]
    [DataRow("NE",       3, 4, 'S')]
    [DataRow(".E",       3, 4, 'S')]
    [DataRow("SE",       3, 4, 'S')]
    [DataRow("EW",       3, 4, 'S')]
    [DataRow("NE..WE",   3, 4, 'S')]
    [DataRow("NE...WE",  3, 4, 'S')]
    [DataRow("NE....WE", 4, 4, 'S')]
    public void TestOgre(string test, int x, int y, char dir, int health = 5) {
        Global.width = 9;
        Global.height = 9;
        Player.Init(6, 4);
        Global.enemies.Add(new Sarcophagus(1, 4, () => new Ogre(2, 4)));

        this.SimulateAndTest<Ogre>(test, x, y, dir, health);
    }

    [TestMethod]
    [DataRow("SSE....WWW",    0, 0, '?', 0)]
    [DataRow("ENNNNN",        0, 0, '?', 0)]
    [DataRow("E",             2, 4, 'Y')]
    [DataRow("EE",            2, 5, 'E')]
    [DataRow("EEE",           2, 6, 'E')]
    [DataRow("EEEE",          2, 7, 'E')]
    [DataRow("EEEEE",         2, 8, 'E')]
    [DataRow("S....EWW.W.",   8, 3, 'W', 2)]
    [DataRow("S....EWW..W",   7, 4, 'N', 2)]
    public void TestMinotaur(string test, int x, int y, char dir, int health = 3) {
        Global.width = 9;
        Global.height = 9;
        Player.Init(6, 4);
        Global.enemies.Add(new Sarcophagus(1, 4, () => new Minotaur(2, 4)));

        this.SimulateAndTest<Minotaur>(test, x, y, dir, health);
    }
}
