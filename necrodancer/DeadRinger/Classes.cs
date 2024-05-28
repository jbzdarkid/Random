
using System.Diagnostics;

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

    public static bool NorthOrSouth(this Direction direction)
        => direction == Direction.North || direction == Direction.South || direction == Direction.NorthSouth;
    public static bool EastOrWest(this Direction direction)
        => direction == Direction.East || direction == Direction.West || direction == Direction.EastWest;
}

public static class Player {
    public static int x, y;
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
        var bell = Global.OccupiedByBell(newX, newY);
        if (bell != null) {
            bell.Ring();
            return true;
        } else {
            var enemy = Global.OccupiedByEnemy(newX, newY);
            if (enemy != null) {
                enemy.OnHit(dir, weaponDamage);
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

    public static void OnHit(Direction dir, int damage) {
        // TODO.
    }
}

public class Enemy {
    public int x, y, health;
    public Direction dir = Direction.EastWest;
    public Enemy(int x, int y, int health) {
        this.x = x;
        this.y = y;
    }

    // Most enemies share logic for movement -- they move axis-aligned (northsouth / eastwest), trying align with the player
    // and will change directions when they align or are blocked.
    public Direction ChangeDirection() {
        if (this.dir.NorthOrSouth()) {
            if      (this.x > Player.x) return Direction.North;
            else if (this.x < Player.x) return Direction.South;
            else if (this.y < Player.y) return Direction.East;
            else if (this.y > Player.y) return Direction.West;
            else Debug.Assert(false);
        } else if (this.dir.EastOrWest()) {
            if      (this.y < Player.y) return Direction.East;
            else if (this.y > Player.y) return Direction.West;
            else if (this.x > Player.x) return Direction.North;
            else if (this.x < Player.x) return Direction.South;
            else Debug.Assert(false);
        } else { // Else, we've already decided a direction, only change if we're blocked
            (var newX, var newY) = this.dir.Add(this.x, this.y);
            if (Global.OccupiedByAnyEnemy(newX, newY)) {
                if (this.dir.EastOrWest()) {
                    if      (this.x > Player.x) return Direction.North;
                    else if (this.x < Player.x) return Direction.South;
                    else return Direction.None; // Do nothing, we are blocked by something but otherwise aligned.
                } else {
                    if      (this.y < Player.y) return Direction.East;
                    else if (this.y > Player.y) return Direction.West;
                    else return Direction.None; // Do nothing, we are blocked by something but otherwise aligned.
                }
            }
        }

        return this.dir; // Keep moving toward the player
    }

    public Direction CanSeePlayer(int range) {
        Direction dir;
        if      (this.x >= Player.x && this.y == Player.y) dir = Direction.North;
        else if (this.x <= Player.x && this.y == Player.y) dir = Direction.South;
        else if (this.x == Player.x && this.y <= Player.y) dir = Direction.East;
        else if (this.x == Player.x && this.y >= Player.y) dir = Direction.West;
        else return Direction.None;

        int distanceToPlayer = Math.Abs(this.x - Player.x) + Math.Abs(this.y - Player.y);
        if (distanceToPlayer > range) return Direction.None;

        var i = this.x;
        var j = this.y;
        while (true) {
            (i, j) = dir.Add(i, j);
            if (Global.OccupiedByAnyEnemy(i, j)) return Direction.None;
            if (Global.OccupiedByPlayer(i, j)) return dir;
        }
    }

    public virtual void Update() {
        // do nothing
    }

    public virtual void OnHit(Direction dir, int damage) {
        this.health -= damage;
        if (this.health <= 0) Global.enemies.Remove(this);
    }
}

public class Dragon : Enemy {
    public int delay = 0;
    public Dragon(int x, int y) : base(x, y, 4) {}

    public override void Update() {
        Direction newDir = this.ChangeDirection();

        if (this.delay > 0) {
            this.delay--;
            if (newDir != Direction.None) this.dir = newDir;
            return;
        }

        if (newDir == Direction.None) return; // We already checked, our current direction is blocked by an enemy.

        (var newX, var newY) = this.dir.Add(this.x, this.y);
        if (Global.OccupiedByAnyEnemy(newX, newY)) return; // Blocked
        if (Global.OccupiedByPlayer(newX, newY)) Player.OnHit(this.dir, 4);
        this.x = newX;
        this.y = newY;
        this.delay = 1;
    }
}

public class Ogre : Enemy {
    public int delay = 0;
    public Direction plannedDirection = Direction.None;
    public Direction swingDir = Direction.None;
    public Ogre(int x, int y) : base(x, y, 10) { }

    public override void Update() {
        if (this.delay > 1) {
            this.delay--;
            return;
        }

        Direction newDir = this.ChangeDirection();

        // If an Ogre spots the player on the beat before they move, they will *plan* to change direction if the player isn't in hitting range next beat.
        if (this.delay == 1) {
            if (newDir != Direction.None) this.plannedDirection = newDir;
            this.delay--;
            return;
        }

        // If we've already committed to a swing, follow through
        if (this.swingDir != Direction.None) {
            int i = this.x;
            int j = this.y;
            for (int k = 0; k < 3; k++) {
                (i, j) = this.swingDir.Add(i, j);
                var bell = Global.OccupiedByBell(i, j);
                if (bell != null) bell.Ring();
                else {
                    var enemy = Global.OccupiedByEnemy(i, j);
                    if (enemy != null) enemy.OnHit(this.swingDir, 5);
                    else if (Global.OccupiedByPlayer(i, j)) {
                        Player.OnHit(this.swingDir, 5);
                    }
                }
            }

            this.swingDir = Direction.None;
            this.delay = 4;
            return;
        }

        // It is now time to move. If the player is in range (3 blocks), ready a swing but *don't* change direction.
        // If the player is out of range, move toward them (in the planned direction).
        Debug.Assert(this.delay == 0);
        Direction swing = this.CanSeePlayer(range: 3);
        if (swing != Direction.None) {
            this.swingDir = swing;
            return;
        }

        // If the player isn't in range, then we get to move.
        (var newX, var newY) = this.plannedDirection.Add(this.x, this.y);
        if (Global.OccupiedByAnyEnemy(newX, newY)) return; // Bonk, will move next frame.
        // It shouldn't be possible for the Ogre to occupy the same space as the player, we would've been able to see them earlier.

        this.x = newX;
        this.y = newY;
        this.delay = 4;
    }
}

public class Nightmare : Enemy {
    public Nightmare(int x, int y) : base(x, y, 6) {
    }
}

public class Minotaur : Enemy {
    public Minotaur(int x, int y) : base(x, y, 6) {
    }
}

/* Don't start here. Start with the minibosses.
public class Skeleton : Enemy {
    Direction dir;
    public Skeleton(int x, int y) : base(x, y) {
        this.delay = 1;
        this.health = 1;
        this.dir = Direction.EastWest;
    }

    public override void Update() {
        if (this.delay > 0) {
            this.delay--;
            return;
        }

        if (this.dir == Direction.NorthSouth && this.x > Player.x) this.dir = Direction.North;
        if (this.dir == Direction.NorthSouth && this.x < Player.x) this.dir = Direction.South;
        if (this.dir == Direction.EastWest && this.y < Player.y) this.dir = Direction.East;
        if (this.dir == Direction.EastWest && this.y > Player.y) this.dir = Direction.West;

        (var newX, var newY) = this.dir.Add(this.x, this.y);
        if (

    }
}
*/

public class Bell {
    public int x;
    public int y;
    public bool rung => this.rungOn != -1;
    private int rungOn = -1;
    Func<int, int, Enemy> summon;
    Enemy? enemy;

    public Bell(int x, int y, Func<int, int, Enemy> summon) {
        this.x = x;
        this.y = y;
        this.summon = summon;
    }

    public void Ring() {
        // Within 9 beats of the last time rung OR miniboss is still alive
        if (Global.beat - this.rungOn < 9 || this.enemy != null) return;
        this.rungOn = Global.beat;

        (int, int)[] spawnTargets = [(this.x + 1, this.y), (this.x, this.y - 1), (this.x, this.y + 1)];
        foreach ((int x, int y) in spawnTargets) {
            if (Global.OccupiedByPlayer(x, y) || Global.OccupiedByDeadRinger(x, y) || Global.OccupiedByEnemy(x, y) != null) continue;
            this.enemy = this.summon(x, y);
            break;
        }

        if (this.enemy == null) {
            (int x, int y) = Global.RandomLocation();
            this.enemy = this.summon(x, y);
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

public class DeadRinger : Enemy {
    public Bell? nextBell;
    public Direction charging = Direction.None;
    public int delay = 0;
    public DeadRinger(int x, int y, Bell nextBell) : base(x, y, 2) {
        this.nextBell = nextBell;
    }

    public override void Update() {
        // Charging direction is immediate, but still respects delay frames.
        if (this.charging == Direction.None) this.charging = this.CanSeePlayer(range: 7);

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        if (this.charging != Direction.None) {
            (var newX, var newY) = this.charging.Add(x, y);
            if (Global.IsOob(newX, newY)) {
                this.charging = Direction.None; // Charge finished. Stun for 1 frame then we'll resume next frame.
                return;
            }
            var bell = Global.OccupiedByBell(newX, newY);
            if (bell != null) {
                Global.bells.Remove(bell); // Destroyed by DR
                this.charging = Direction.None;
                this.delay = 1;
                return;
            }
            var enemy = Global.OccupiedByEnemy(newX, newY);
            if (enemy != null) {
                // TODO: Probably DR kills things when he charges them idk
                this.charging = Direction.None;
                return;
            }

            this.x = newX;
            this.y = newY;
            return;
        }

        if (this.nextBell != null) {
            if (this.x == this.nextBell.x - 1 && this.y == this.nextBell.y) {
                // Ring the bell
                this.nextBell.Ring();
                int currentIndex = Global.bells.IndexOf(nextBell);
                int nextIndex = (currentIndex + 1) % Global.bells.Count;
                this.nextBell = Global.bells[nextIndex];
                return;
            }

            // Move diagonally toward the square north of the bell
            var newX = this.x;
            if      (this.x < this.nextBell.x - 1) newX = this.x + 1;
            else if (this.x > this.nextBell.x - 1) newX = this.x - 1;
            var newY = this.y;
            if      (this.y < nextBell.y) newY = this.y + 1;
            else if (this.y > nextBell.y) newY = this.y - 1;

            if (Global.OccupiedByBell(newX, newY) != null || Global.OccupiedByEnemy(newX, newY) != null) {
                newY = this.y; // not sure if correct. whatevs.
            }

            this.x = newX;
            this.y = newY;
            this.delay = 1;
            if (this.x == this.nextBell.x - 1 && this.y == this.nextBell.y) delay++; // Extra delay for ringing the bell. I think this works.
        }
    }

    public override void OnHit(Direction dir, int damage) {
        if (damage < 999) return;
        // TODO: Phase change on inf damage
    }
}
