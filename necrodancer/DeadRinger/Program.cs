using System.Text;

public static class Global {
    public static List<Bell> bells = [];
    public static List<Enemy> enemies = [];
    public static int beat = 0;

    public static Bell? OccupiedByBell(int x, int y) =>
        bells.Find(bell => bell.x == x && bell.y == y);
    public static Enemy? OccupiedByEnemy(int x, int y) =>
        enemies.Find(enemy => enemy.x == x && enemy.y == y);
    public static bool OccupiedByDeadRinger(int x, int y) =>
        x == DeadRinger.x && y == DeadRinger.y;
    public static bool OccupiedByPlayer(int x, int y) =>
        x == Player.x && y == Player.y;

    public static bool IsOob(int x, int y) {
        if (y < 0 || y > 11 || x < 0) return true;
        if (Player.x == 10) return x == 10 && (y < 4 || y > 6);
        return x > 9;
    }
}

public static class Program {
    public static void Init() {
        Global.bells = [new(3, 2, "dragon"), new(3, 8, "ogre"), new(8, 8, "mino"), new(8, 2, "mare")];
        if (RNG.Get(2) == 0) {
            DeadRinger.Init(4, 3, Global.bells[0]);
        } else {
            DeadRinger.Init(4, 7, Global.bells[1]);
        }

        Player.Init(10, 5);
    }

    public static void Update() {
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
                Global.enemies.Add(new Enemy(type, 0, 10));
            } else {
                Global.enemies.Add(new Enemy(type, 1, 11));
            }
        }

        DeadRinger.Update();

        foreach (var enemy in Global.enemies) {
            enemy.Update();
        }
    }

    public static void DrawGrid() {
        StringBuilder output = new("+-----------+\n");
        for (int x = 0; x < 10; x++) {
            output.Append('|');
            for (int y = 0; y < 11; y++) {
                var bell = Global.OccupiedByBell(x, y);
                var enemy = Global.OccupiedByEnemy(x, y);
                if (bell != null) output.Append(bell.rung ? 'B' : 'b');
                else if (enemy != null) output.Append(enemy.type[0]);
                else if (Global.OccupiedByPlayer(x, y)) output.Append('P');
                else if (Global.OccupiedByDeadRinger(x, y)) output.Append('D');
                else output.Append(' ');
            }
            output.Append("|\n");
        }
        if (Player.x == 10) {
            output.Append("+----");
            for (int y = 4; y < 7; y++) {
                if (Global.OccupiedByPlayer(10, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("----+\n");
        } else {
            output.Append("+-----------+\n");
        }
        Console.Write(output.ToString());
    }

    public static void Main() {
        Init();
        Global.beat = 0;
        while (true) {
            DrawGrid();
            Console.Write($"Beat: {Global.beat}, Input: ");
            // Get player input. TODO: Implement bomb, earth, drum
            bool droppedTheBeat;
            while (!Player.HandleInput(Console.ReadKey().Key, out droppedTheBeat)) continue;
            Console.Write("\n"); // newline after the input is read successfully
            if (droppedTheBeat) Console.WriteLine("Dropped the beat!");

            if (Player.x == 10) continue;

            // Once the player has entered the room, start the fight.
            Update(); // Update enemies
            Global.beat++;
        }
    }
}