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
        _ => Direction.None,
    };

    private void Simulate(string directions) {
        foreach (char c in directions) {
            Player.Move(C2D(c));
            List<Enemy> enemies = new(Global.enemies); // To allow additions during enumeration
            enemies.ForEach(enemy => enemy.Update());
        }
    }

    [TestMethod]
    [DataRow("E",           2, 4, 'E')]
    [DataRow("EE",          2, 5, 'E')]
    [DataRow("EEE",         2, 5, 'E')]
    [DataRow("EEEE",        2, 6, 'E')]
    [DataRow("EW",          3, 4, 'S')]
    [DataRow("EEWW",        3, 5, 'S')]
    [DataRow("NNNSNSNN",    0, 0, 'X')]
    [DataRow("NNNNNN",      0, 0, 'X')]
    [DataRow("NN.ENNNNW..", 2, 4, 'N')]
    public void TestGreenDragon(string test, int x, int y, char dir) {
        Global.width = 9;
        Global.height = 9;
        Player.Init(6, 4);
        Global.enemies.Add(new Sarcophagus(1, 4, () => new Dragon(2, 4)));

        Debug.WriteLine($"Simulating test '{test}'");
        this.Simulate(test);
        var dragon = Global.enemies.Find(x => x is Dragon) as Dragon;
        if (dir == 'X') { // Killed.
            Assert.IsNull(dragon);
        } else {
            Assert.IsNotNull(dragon);
            Assert.AreEqual(x, dragon.x);
            Assert.AreEqual(y, dragon.y);
            Assert.AreEqual(C2D(dir), dragon.dir);
        }
    }

    [TestMethod]
    public void TestOgre() {
        Global.enemies.Add(new Ogre(2, 5));

        Player.Init(10, 5);

        this.Simulate("NNNEEE");

    }
}
