
public enum Direction {
    None = 0,

    North = 1,
    South = 4,
    East = 2,
    West = 3,
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
}

public static class Player {
    public static int x, y;
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
        var bell = Global.OccupiedByBell(newX, newY);
        if (bell != null) {
            bell.Ring();
            return true;
        } else {
            var enemy = Global.OccupiedByEnemy(newX, newY);
            if (enemy != null) {
                enemy.HitByPlayer(dir);
                return true;
            }
        }

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
}

public class Enemy {
    public int x, y, health;
    public string type;
    public Enemy(string type, int x, int y) {
        this.type = type;
        this.x = x;
        this.y = y;
    }

    public void Update() {
        if (this.type == "skele")
        {
        } else if (this.type == "armor")
        {
        } else if (this.type == "mage")
        {
        } else if (this.type == "rider")
        {
        }
    }

    public void HitByPlayer(Direction dir) {
        // TODO
    }
}

public class Bell {
    public int x;
    public int y;
    public bool rung => this.rungOn != -1;
    private int rungOn = -1;
    public string enemyType;

    public Bell(int x, int y, string enemyType) {
        this.x = x;
        this.y = y;
        this.enemyType = enemyType;
    }

    public void Ring() {
        // Within 9 beats of the last time rung OR miniboss is still alive
        if (Global.beat - this.rungOn < 9 || Global.enemies.Exists(enemy => enemy.type == this.enemyType)) return;
        this.rungOn = Global.beat;

        (int, int)[] spawnTargets = [(this.x + 1, this.y), (this.x, this.y - 1), (this.x, this.y + 1)];
        foreach ((int x, int y) in spawnTargets) {
            if (Global.OccupiedByPlayer(x, y) || Global.OccupiedByDeadRinger(x, y) || Global.OccupiedByEnemy(x, y) != null) continue;

        }
    }
}

public static class RNG {
    private static Random random = new();
    public static void Seed(int seed) {
        random = new Random(seed);
    }

    public static int Get(int max) => random.Next() % max;
}

public static class DeadRinger {
    public static int x, y;
    public static Bell? nextBell;
    public static Direction charging = Direction.None;
    public static void Init(int x_, int y_, Bell bell_) {
        x = x_;
        y = y_;
        nextBell = bell_;
    }

    public static void Update() {
        if (charging != Direction.None) {
            (var newX, var newY) = charging.Add(x, y);
            if (Global.IsOob(newX, newY)) {
                charging = Direction.None; // Charge finished. Stun for 1 frame then we'll resume next frame.
                return;
            }
            var bell = Global.OccupiedByBell(newX, newY);
            if (bell != null) {
                Global.bells.Remove(bell); // Destroyed by DR
                charging = Direction.None;
                return;
            }
            var enemy = Global.OccupiedByEnemy(newX, newY);
            if (enemy != null) {
                // TODO: Probably DR kills things when he charges them idk
                charging = Direction.None;
                return;
            }

            x = newX;
            y = newY;
            return;
        }

        if (Global.beat % 2 == 1) return; // I think it's more complicated than this cuz stalls are adjusted by charging

        Direction toCharge = CanSeePlayer();
        if (toCharge != Direction.None) {
            charging = toCharge;
            return;
        }

        if (nextBell != null) {
            if (x == nextBell.x - 1 && y == nextBell.y) {
                // Ring the bell
                nextBell.Ring();
                return;
            }

            // Move diagonally toward the square north of the bell
            var newX = x;
            if (x < nextBell.x - 1) newX = x - 1;
            else if (x > nextBell.x + 1) newX = x + 1;
            var newY = y;
            if (y < nextBell.y) newY = y - 1;
            if (y > nextBell.y) newY = y + 1;

            if (Global.OccupiedByBell(newX, newY) != null || Global.OccupiedByEnemy(newX, newY) != null) {
                // TODO: idk man, adjust newX/newY somehow I think
            }

            x = newX;
            y = newY;
        }
    }

    public static Direction CanSeePlayer() {
        // Player is north 
        if (x == Player.x && y - 6 >= Player.y) {
            for (int j = Player.y + 1; j < y; j++) {
                if (Global.OccupiedByBell(x, j) != null || Global.OccupiedByEnemy(x, j) != null) return Direction.None;
            }
            return Direction.North;
        }
        // Player is south 
        else if (x == Player.x && y + 6 <= Player.y)
        {
            for (int j = y + 1; j < Player.y; j++)
            {
                if (Global.OccupiedByBell(x, j) != null || Global.OccupiedByEnemy(x, j) != null) return Direction.None;
            }
            return Direction.South;
        }
        // Player is west 
        else if (x - 6 >= Player.x && y == Player.y)
        {
            for (int i = Player.x + 1; i < x; i++)
            {
                if (Global.OccupiedByBell(i, y) != null || Global.OccupiedByEnemy(i, y) != null) return Direction.None;
            }
            return Direction.West;
        }
        // Player is east 
        else if (x + 6 <= Player.x && y == Player.y)
        {
            for (int i = x; i < Player.x; i++)
            {
                if (Global.OccupiedByBell(i, y) != null || Global.OccupiedByEnemy(i, y) != null) return Direction.None;
            }
            return Direction.East;
        }

        // Not cardinally aligned
        return Direction.None;
    }
}

