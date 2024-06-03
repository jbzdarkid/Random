using System.Diagnostics;

namespace DeadRinger;

public class Enemy {
    public int x, y, health, delay;
    public Direction dir = Direction.EastWest;
    public Enemy(int x, int y, int health, int delay) {
        this.x = x;
        this.y = y;
        this.health = health;
        this.delay = delay;
    }

    // Most enemies share logic for movement -- they move axis-aligned (northsouth / eastwest)
    // until they line up with the player on the perpendicular axis.
    // They can change axis when blocked by an enemy or wall.
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
        // no default behavior
    }

    public virtual void OnHit(Direction dir, int damage) {
        this.health -= damage;
        if (this.health <= 0) Global.enemies.Remove(this);
    }
}

public class BasicMiniboss : Enemy {
    public int damage = 0;
    public BasicMiniboss(int x, int y, int health, int damage, int delay = 1) : base(x, y, health, delay) {
        this.damage = damage;
    }

    public override void Update() {
        Direction newDir = this.ChangeDirection();
        if (newDir != Direction.None) this.dir = newDir;

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        if (newDir == Direction.None) return; // We already checked and found that our current direction is blocked by an enemy.

        (var newX, var newY) = this.dir.Add(this.x, this.y);
        if (Global.OccupiedByAnyEnemy(newX, newY)) return; // Blocked
        if (Global.OccupiedByPlayer(newX, newY)) {
            Player.OnHit(this.dir, this.damage);
            this.delay = 1;
            return;
        }

        this.x = newX;
        this.y = newY;
        this.delay = 1;
    }
}

public class GreenDragon : BasicMiniboss {
    public GreenDragon(int x, int y, int delay = 1) : base(x, y, health: 4, damage: 4, delay) { }
}

public class Nightmare : BasicMiniboss {
    public Nightmare(int x, int y, int delay = 1) : base(x, y, health: 3, damage: 4, delay) { }
}

public class BloodNightmare : BasicMiniboss {
    public BloodNightmare(int x, int y, int delay = 1) : base(x, y, health: 5, damage: 5, delay) { }
}

public class Ogre : Enemy {
    public bool cannotSwing = true; // Ogres are not allowed to swing at the player until they've moved once (to avoid jumpscares)
    public Direction swinging = Direction.None;
    public Direction plannedDir = Direction.None;
    public Ogre(int x, int y, int delay = 1) : base(x, y, 5, delay) { }

    // Ogres will make 90 degree inside turns if the player is close to axis-aligned.
    public Direction PlanDirectionChange() {
        if (this.dir == Direction.North && this.x.Between(Player.x - 1, Player.x)) {
            if (this.y < Player.y) return Direction.East;
            if (this.y > Player.y) return Direction.West;
        } else if (this.dir == Direction.South && this.x.Between(Player.x, Player.x + 1)) {
            if (this.y < Player.y) return Direction.East;
            if (this.y > Player.y) return Direction.West;
        } else if (this.dir == Direction.NorthSouth && this.x == Player.x) {
            if (this.y < Player.y) return Direction.East;
            if (this.y > Player.y) return Direction.West;
        } else if (this.dir == Direction.East && this.y.Between(Player.y, Player.y + 1)) {
            if (this.x > Player.x) return Direction.North;
            if (this.x < Player.x) return Direction.South;
        } else if (this.dir == Direction.West && this.y.Between(Player.y - 1, Player.y)) {
            if (this.x > Player.x) return Direction.North;
            if (this.x < Player.x) return Direction.South;
        } else if (this.dir == Direction.EastWest && this.y == Player.y) {
            if (this.x > Player.x) return Direction.North;
            if (this.x < Player.x) return Direction.South;
        }

        return Direction.None;
    }
    
    public override void Update() {
        // If the player is immediately adjacent (i.e. would block our movement), overrite the instant swing prevention.
        if (this.cannotSwing) {
            if (Global.OccupiedByPlayer(this.x - 1, this.y)
                || Global.OccupiedByPlayer(this.x + 1, this.y)
                || Global.OccupiedByPlayer(this.x, this.y + 1)
                || Global.OccupiedByPlayer(this.x, this.y - 1)) this.cannotSwing = false;
        }

        // Ogres plan certain actions one beat in advance.
        if (this.delay == 1) {
            if (!this.cannotSwing) this.swinging = this.CanSeePlayer(range: 3);
            if (this.swinging == Direction.None) this.plannedDir = this.PlanDirectionChange();
        }

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        // Ogres can also read a swing on the beat they move. If this happens, we still delay a beat before the next swing.
        if (!this.cannotSwing && this.swinging == Direction.None) {
            this.swinging = this.CanSeePlayer(range: 3);
            if (this.swinging != Direction.None) {
                this.delay = 1;
                return;
            }
        }

        this.cannotSwing = false; // Even if we don't move because we were blocked by an enemy, this restriction only applies once.

        // If we've already committed to a swing, follow through
        if (this.swinging != Direction.None) {
            int i = this.x;
            int j = this.y;
            for (int k = 0; k < 3; k++) {
                (i, j) = this.swinging.Add(i, j);
                var bell = Global.OccupiedByBell(i, j);
                if (bell != null) bell.Ring();
                else {
                    var enemy = Global.OccupiedByEnemy(i, j);
                    if (enemy != null) enemy.OnHit(this.swinging, 5);
                    else if (Global.OccupiedByPlayer(i, j)) Player.OnHit(this.swinging, 5);
                }
            }

            this.swinging = Direction.None;
            this.delay = 3;
            return;
        }
        
        // Finally, if we aren't readying a swing or following through, we move in either our planned direction or the existing one.
        Direction newDir = this.plannedDir;
        if (newDir == Direction.None) newDir = this.ChangeDirection();
        if (newDir == Direction.None) return; // We checked and found that our current direction is blocked by an enemy.
        this.dir = newDir;
        this.plannedDir = Direction.None;

        (var newX, var newY) = this.dir.Add(this.x, this.y);
        if (Global.OccupiedByAnyEnemy(newX, newY)) return; // Blocked
        this.x = newX;
        this.y = newY;
        this.delay = 3;
    }
}

public class Minotaur : Enemy {
    Direction charging = Direction.None;
    public Minotaur(int x, int y, int delay = 1) : base(x, y, 3, delay) { }

    public override void Update() {
        if (this.delay > 1) {
            this.delay--;
            return;
        }

        // Minotaurs can ready a charge if they see the player right as they stand up (delay = 1)
        // or while generally moving around (delay = 0)
        if (this.charging == Direction.None) this.charging = this.CanSeePlayer(range: 6);

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        int newX, newY;
        if (this.charging != Direction.None) {
            this.dir = this.charging; // Just for clarity / testing purposes, charging is still the source of truth.
            (newX, newY) = this.charging.Add(x, y);
            Bell? bell = null;
            if (!Global.IsOob(newX, newY)
                && !Global.OccupiedByPlayer(newX, newY)
                && (bell = Global.OccupiedByBell(newX, newY)) == null
                && !Global.OccupiedByAnyEnemy(newX, newY)) {
                // Charge is not obstructed, keep on charging
                this.x = newX;
                this.y = newY;
                return;
            }

            bell?.Ring(); // Minotaurs ring bells if they charge into them

            // When a minotaur finishes charging, it swaps to the perpendicular axis.
            // Note that this is just the preferred direction, it will charge if the player is aligned in any direction.
            if (this.charging.EastOrWest()) this.dir = Direction.NorthSouth;
            else if (this.charging.NorthOrSouth()) this.dir = Direction.EastWest;
            this.charging = Direction.None;
            this.delay = 2;
            return;
        }

        var newDir = this.ChangeDirection();
        if (newDir == Direction.None) return; // We already checked and found that our current direction is blocked by an enemy.
        this.dir = newDir;

        (newX, newY) = this.dir.Add(this.x, this.y);
        if (Global.OccupiedByAnyEnemy(newX, newY)) return; // Blocked

        this.x = newX;
        this.y = newY;
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

public class DeadRinger : Enemy {
    public Bell? nextBell;
    public Direction charging = Direction.None;
    public DeadRinger(int x, int y, Bell nextBell) : base(x, y, 2, 0) {
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
            this.dir = this.charging; // Just for clarity / testing purposes, charging is still the source of truth.
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

public class Sarcophagus : Enemy {
    public Func<Enemy> summon;
    public Enemy? enemy;
    public Sarcophagus(int x, int y, Func<Enemy> summon) : base(x, y, 8, 0) {
        this.summon = summon;
    }

    public override void Update() {
        if (this.delay > 0) {
            this.delay--;
            return;
        }

        if (this.enemy == null) {
            this.enemy = this.summon();
            Global.enemies.Add(this.enemy);
            this.enemy.Update();
        }
        this.delay = 8;
    }
}
