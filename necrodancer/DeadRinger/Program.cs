using System.Diagnostics;
using System.Text;

namespace DeadRinger;

public static class Global {
    public static List<Bell> bells = [];
    public static List<Enemy> enemies = [];
    public static int beat = 0;
    public static DeadRinger DeadRinger = new(-1, -1, null);

    public static int width = 11;
    public static int height = 10;
    public static bool IsOob(int x, int y) {
        if (y < 0 || y >= width || x < 0) return true;
        if (Player.x == height) return x == height && (y < 4 || y > 6);
        return x >= height;
    }

    public static Bell? OccupiedByBell(int x, int y) =>
        bells.Find(bell => bell.x == x && bell.y == y);
    public static Enemy? OccupiedByEnemy(int x, int y) =>
        enemies.Find(enemy => enemy.x == x && enemy.y == y);
    public static bool OccupiedByDeadRinger(int x, int y) =>
        x == DeadRinger.x && y == DeadRinger.y;
    public static bool OccupiedByAnyEnemy(int x, int y) => 
        OccupiedByDeadRinger(x, y) || OccupiedByBell(x, y) != null || OccupiedByEnemy(x, y) != null;
    public static bool OccupiedByPlayer(int x, int y) =>
        x == Player.x && y == Player.y;


    public static (int, int) RandomLocation() {
        return (1, 1); // TODO.
    }
}

public static class Program {
    public static void Init() {
        Global.bells = [
            new(3, 2, (x, y) => new Dragon(x, y, delay: 0)),
            new(3, 8, (x, y) => new Ogre(x, y)),
            new(8, 2, (x, y) => new Nightmare(x, y)),
            new(8, 8, (x, y) => new Minotaur(x, y)),
        ];
        if (RNG.Get(2) == 0) {
            Global.DeadRinger = new(4, 3, Global.bells[0]);
        } else {
            Global.DeadRinger = new(4, 7, Global.bells[1]);
        }

        Player.Init(10, 5);
    }

    public static void DrawGrid() {
        StringBuilder output = new("+" + new string('-', Global.width) + "+\n");
        for (int x = 0; x < Global.height; x++) {
            output.Append('|');
            for (int y = 0; y < Global.width; y++) {
                var bell = Global.OccupiedByBell(x, y);
                var enemy = Global.OccupiedByEnemy(x, y);
                if (bell != null) output.Append(bell.rung ? 'B' : 'b');
                else if (enemy != null) output.Append(char.ToLowerInvariant(enemy.GetType().Name?[0] ?? '?'));
                else if (Global.OccupiedByPlayer(x, y)) output.Append('P');
                else if (Global.OccupiedByDeadRinger(x, y)) output.Append('D');
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

            List<Enemy> enemies = new(Global.enemies); // To allow additions during enumeration
            foreach (var enemy in enemies) enemy.Update();
        }
    }

    public static void Main() {
        Simulate();

        RNG.Seed(0);
        Init();
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

            Global.DeadRinger.Update();
            foreach (var enemy in Global.enemies) enemy.Update();
            Global.beat++;
        }
    }
}