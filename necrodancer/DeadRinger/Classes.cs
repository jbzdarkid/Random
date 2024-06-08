namespace DeadRinger;

public enum Direction {
    None = 0,

    North = 1,
    South = 4,
    East = 2,
    West = 3,

    NorthSouth = 6,
    EastWest = 7,
}

public static class DirectionExtensions {
    public static (int, int) Add(this Direction direction, int x, int y)
    => direction switch {
        Direction.North => (x - 1, y),
        Direction.South => (x + 1, y),
        Direction.East => (x, y + 1),
        Direction.West => (x, y - 1),
        _ => (x, y),
    };
    public static (int, int) Subtract(this Direction direction, int x, int y)
    => direction switch {
        Direction.North => (x + 1, y),
        Direction.South => (x - 1, y),
        Direction.East => (x, y - 1),
        Direction.West => (x, y + 1),
        _ => (x, y),
    };
    public static bool NorthOrSouth(this Direction direction)
        => direction == Direction.North || direction == Direction.South || direction == Direction.NorthSouth;
    public static bool EastOrWest(this Direction direction)
        => direction == Direction.East || direction == Direction.West || direction == Direction.EastWest;
}

public static class IntExtensions {
    // Inclusive on min and max.
    public static bool Between(this int val, int min, int max) => val >= min && val <= max;
}

public static class Player {
    public static int x, y;
    public static int previousX, previousY; // Some enemies care about this, sadly.
    public static int weaponDamage = 1; // TODO: Starting with base dagger for now
    public static void Init(int x_, int y_) {
        x = x_;
        y = y_;
    }

    /// <summary>
    /// Move the player in a specified |direction|
    /// </summary>
    /// <returns>False if you drop the beat</returns>
    public static bool Move(Direction dir) {
        if (dir == Direction.None) return false;

        (var newX, var newY) = dir.Add(x, y);
        if (Global.IsOob(newX, newY)) return false;
        if (Global.OccupiedByEnemy(newX, newY, out Enemy? enemy)) {
            enemy.OnHit(dir, weaponDamage);
            return true;
        }

        previousX = x;
        previousY = y;
        x = newX;
        y = newY;
        return true;
    }

    public static void Special(string v) => throw new NotImplementedException();

    public static bool HandleInput(ConsoleKey key, out bool droppedTheBeat) {
        droppedTheBeat = false;

        switch (key) {
            case ConsoleKey.E:
                droppedTheBeat = !Move(Direction.North);
                return true;
            case ConsoleKey.S:
                droppedTheBeat = !Move(Direction.West);
                return true;
            case ConsoleKey.D:
                droppedTheBeat = !Move(Direction.South);
                return true;
            case ConsoleKey.F:
                droppedTheBeat = !Move(Direction.East);
                return true;
            case ConsoleKey.Spacebar:
                droppedTheBeat = !Move(Direction.None);
                return true;
            case ConsoleKey.Q:
                Special("bomb");
                return true;
            case ConsoleKey.A:
                Special("drum");
                return true;
            case ConsoleKey.W:
                Special("earth");
                return true;
        }

        return false;
    }

    public static void OnHit(Direction dir, int damage) {
        // TODO.
    }
}

public static class RNG {
    private static Random random = new();
    private static Queue<int> values = [];
    public static void Seed(int seed) {
        random = new Random(seed);
    }

    public static void Seed(ReadOnlySpan<int> args) {
        foreach (var value in args) values.Enqueue(value);
    }

    public static int Get(int max) {
        if (values.Count > 0) return values.Dequeue() % max;
        return random.Next() % max;
    }
}