using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Text;

namespace DeadRinger;

public static class Global {
    public static List<Enemy> enemies = [];
    public static List<Enemy> newEnemies = []; // A separate list of enemies spawned during this beat, to be added after enemies are updated.
    public static List<Enemy> oldEnemies = []; // A separate list of enemies removed during this beat, to be deleted after enemies are updated.
    public static int beat = 0;

    public static int width = 11;
    public static int height = 10;
    public static bool IsOob(int x, int y) {
        if (y < 0 || y >= width || x < 0) return true;
        if (Player.x == height) return x == height && (y < 4 || y > 6);
        return x >= height;
    }

    public static void SimulateBeat() {
        foreach (var enemy in enemies) enemy.Update();

        // TODO: Enemy priority goes here, use SortedList.
        enemies.RemoveAll(oldEnemies.Contains);
        enemies.AddRange(newEnemies);
        newEnemies.Clear();
        oldEnemies.Clear();
        beat++;
    }

    public static bool OccupiedByEnemy(int x, int y, [NotNullWhen(returnValue: true)] out Enemy? enemy) => OccupiedByEnemy<Enemy>(x, y, out enemy);
    public static bool OccupiedByEnemy<T>(int x, int y, [NotNullWhen(returnValue: true)] out T? enemy) where T : Enemy {
        enemy = enemies.Find(enemy => enemy.x == x && enemy.y == y) as T;
        return enemy != null;
    }
    public static bool OccupiedByPlayer(int x, int y) => x == Player.x && y == Player.y;


    public static (int, int) RandomLocation() {
        return (1, 1); // TODO.
    }
}

public static class Program {
    public static void InitDeadRinger() {
        Global.enemies.Add(new Bell(3, 2, (x, y) => new GreenDragon(x, y, delay: 0)));
        Global.enemies.Add(new Bell(3, 8, (x, y) => new Ogre       (x, y, delay: 0)));
        Global.enemies.Add(new Bell(8, 2, (x, y) => new Nightmare  (x, y, delay: 0)));
        Global.enemies.Add(new Bell(8, 8, (x, y) => new Minotaur   (x, y, delay: 0)));
        if (RNG.Get(2) == 0) {
            Global.enemies.Add(new DeadRinger(4, 3, (Bell)Global.enemies[0]));
        } else {
            Global.enemies.Add(new DeadRinger(4, 7, (Bell)Global.enemies[1]));
        }

        Player.Init(10, 5);
    }

    public static void DrawGrid() {
        StringBuilder output = new("+" + new string('-', Global.width) + "+\n");
        for (int x = 0; x < Global.height; x++) {
            output.Append('|');
            for (int y = 0; y < Global.width; y++) {
                if (Global.OccupiedByEnemy(x, y, out Enemy? enemy)) {
                    if (enemy is Bell bell) output.Append(bell.rung ? 'B' : 'b');
                    else if (enemy is DeadRinger deadRinger) output.Append(deadRinger.phase2 ? 'D' : 'd');
                    else output.Append(char.ToLowerInvariant(enemy.GetType().Name?[0] ?? '?'));
                }
                else if (Global.OccupiedByPlayer(x, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("|\n");
        }
        if (Player.x == Global.height) {
            output.Append("+----");
            for (int y = 4; y < 7; y++) {
                if (Global.OccupiedByPlayer(Global.height, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("----+\n");
        } else {
            output.Append("+" + new string('-', Global.width) + "+\n");
        }
        Console.Write(output.ToString());
        Debug.WriteLine(output.ToString());
    }

    public static void Simulate() {
        while (Global.enemies.Count > 0) {
            DrawGrid();
            Console.Write($"Beat: {Global.beat}, Input: ");
            ConsoleKeyInfo input = Console.ReadKey();
            while (!Player.HandleInput(input.Key, out _)) continue;

            Console.Write("\n"); // newline after the input is read successfully
            Global.SimulateBeat();
        }
    }

    public static void Main() {
        Simulate();

        RNG.Seed(0);
        InitDeadRinger();
        Global.beat = 0; // 100 beats should be enough, since lures is only like 80 or so.
        while (true) {
            DrawGrid();
            Console.Write($"Beat: {Global.beat}, Input: ");
            bool droppedTheBeat;
            while (!Player.HandleInput(Console.ReadKey().Key, out droppedTheBeat)) continue;
            Console.Write("\n"); // newline after the input is read successfully
            if (droppedTheBeat) Console.WriteLine("Dropped the beat!");

            if (Player.x == 10) continue; // Still in the entryway, fight hasn't started yet.
            /* Don't start here. Start with the minibosses.
            if (Global.beat % 8 == 0) {
                // Top left sarc
                var rng = RNG.Get(8);
                var type = new string[] { "skele", "armor", "mage", "rider" }[rng % 4];
                if (rng / 4 == 0) {
                    Global.enemies.Add(new Enemy(type, 0, 1));
                } else {
                    Global.enemies.Add(new Enemy(type, 1, 0));
                }
               
                // Top right sarc
                rng = RNG.Get(8);
                type = new string[] { "skele", "armor", "mage", "rider" }[rng % 4];
                if (rng / 4 == 0) {
                    Global.enemies.Add(new Enemy(type, 0, 9));
                } else {
                    Global.enemies.Add(new Enemy(type, 1, 10));
               }
            }
            */

            Global.SimulateBeat();
        }
    }
}