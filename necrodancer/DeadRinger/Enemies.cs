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
            if (Global.OccupiedByEnemy(newX, newY, out _)) {
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

    public Direction CanSeePlayer(int range) => this.CanSeeTarget(Player.x, Player.y, range);
    public Direction CanSeePreviousPlayerPosition(int range) => this.CanSeeTarget(Player.previousX, Player.previousY, range);
    public Direction CanSeeTarget(int x, int y, int range) {
        // Start with a sanity check that we're in a straight line, and within range
        Direction dir;
        if      (this.x >= x && this.y == y) dir = Direction.North;
        else if (this.x <= x && this.y == y) dir = Direction.South;
        else if (this.x == x && this.y <= y) dir = Direction.East;
        else if (this.x == x && this.y >= y) dir = Direction.West;
        else return Direction.None;

        int distanceToPlayer = Math.Abs(this.x - x) + Math.Abs(this.y - y);
        if (distanceToPlayer > range) return Direction.None;

        // Then iterate all the squares between here and there.
        var i = this.x;
        var j = this.y;
        while (true) {
            (i, j) = dir.Add(i, j);
            if (Global.OccupiedByEnemy(i, j, out _)) return Direction.None;
            if (i == x && j == y) return dir;
        }
    }

    public virtual void Update() {
        // no default behavior
    }

    public virtual void OnHit(Direction dir, int damage) {
        this.health -= damage;
        if (this.health <= 0) Global.oldEnemies.Add(this);
    }
}

public class BasicMiniboss : Enemy {
    public int damage = 0;
    public BasicMiniboss(int x, int y, int health, int damage, int delay = 1) : base(x, y, health, delay) {
        this.damage = damage;
    }

    public override void Update() {
        // Check to see if we aligned with the player (or their previous position), in which case we trigger a direction change.
        if      (this.y == Player.y && this.x > Player.x) this.dir = Direction.North;
        else if (this.y == Player.y && this.x < Player.x) this.dir = Direction.South;
        else if (this.x == Player.x && this.y < Player.y) this.dir = Direction.East;
        else if (this.x == Player.x && this.y > Player.y) this.dir = Direction.West;
        else if (this.y == Player.previousY && this.x > Player.previousX) this.dir = Direction.North;
        else if (this.y == Player.previousY && this.x < Player.previousX) this.dir = Direction.South;
        else if (this.x == Player.previousX && this.y < Player.previousY) this.dir = Direction.East;
        else if (this.x == Player.previousX && this.y > Player.previousY) this.dir = Direction.West;

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        // Try to move in our current direction
        (var newX, var newY) = this.dir.Add(this.x, this.y);
        if (Global.OccupiedByPlayer(newX, newY)) {
            Player.OnHit(this.dir, this.damage);
            this.delay = 1;
            return;
        }

        // If there's an enemy blocking us, consider changing direction
        if (Global.OccupiedByEnemy(newX, newY, out _)) {
            if (this.dir.NorthOrSouth()) {
                if      (this.x > Player.x) this.dir = Direction.North;
                else if (this.x < Player.x) this.dir = Direction.South;
            } else if (this.dir.EastOrWest()) {
                if      (this.x < Player.y) this.dir = Direction.East;
                else if (this.x > Player.y) this.dir = Direction.West;
            }

            if (Global.OccupiedByEnemy(newX, newY, out _)) return;
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
                if (Global.OccupiedByEnemy(i, j, out Enemy? enemy)) enemy.OnHit(this.swinging, 5);
                else if (Global.OccupiedByPlayer(i, j)) Player.OnHit(this.swinging, 5);
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
        if (Global.OccupiedByEnemy(newX, newY, out _)) return; // Blocked
        this.x = newX;
        this.y = newY;
        this.delay = 3;
    }
}

public class Minotaur : Enemy {
    Direction charging = Direction.None;
    public Minotaur(int x, int y, int delay = 1) : base(x, y, 3, delay) { }

    public override void Update() {
        if (this.delay > 0) {
            this.delay--;
            return;
        }

        // Minotaurs will charge at the player's last known position as well as their current position.
        if (this.charging == Direction.None) this.charging = this.CanSeePlayer(range: 6);
        if (this.charging == Direction.None) this.charging = this.CanSeePreviousPlayerPosition(range: 6);

        int newX, newY;
        if (this.charging != Direction.None) {
            this.dir = this.charging; // Just for clarity / testing purposes, charging is still the source of truth.
            (newX, newY) = this.charging.Add(this.x, this.y);
            Enemy? enemy = null;
            if (!Global.IsOob(newX, newY)
                && !Global.OccupiedByPlayer(newX, newY)
                && !Global.OccupiedByEnemy(newX, newY, out enemy)) {
                // Charge is not obstructed, keep on charging
                this.x = newX;
                this.y = newY;
                return;
            }
            
            // Minotaurs ring bells if they charge into them, but don't damage other enemies.
            if (Global.OccupiedByPlayer(newX, newY)) Player.OnHit(this.charging, 4);
            if (enemy is Bell bell) bell.OnHit(this.charging, 4);

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
        if (Global.OccupiedByEnemy(newX, newY, out _)) return; // Blocked

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
    public Direction ringBell = Direction.None;
    public bool phase2 = false;
    public DeadRinger(int x, int y, Bell nextBell) : base(x, y, 2, 0) {
        this.nextBell = nextBell;
    }

    public override void Update() {
        // If we know there's no next bell (because we rang it), proceed to phase 2.
        if (!this.phase2 && this.nextBell == null) this.phase2 = true;
        // If the last bell was rung by the player (or we destroyed it), proceed to phase 2.
        if (!this.phase2 && !Global.enemies.Exists(x => x is Bell bell && !bell.rung)) this.phase2 = true;
        // Proceed with the appropriate phase.
        if (!this.phase2) this.UpdatePhase1();
        else              this.UpdatePhase2();
    }

    public void PickNextBell() {
        if (this.nextBell == null) return; // All bells already run/destroyed.

        Bell? nextBell = null;
        bool foundThisBell = false;
        foreach (var enemy in Global.enemies) {
            if (enemy.x == this.nextBell.x && enemy.y == this.nextBell.y) {
                foundThisBell = true;
                continue;
            } else if (foundThisBell && enemy is Bell bell) {
                nextBell = bell; // Dead ringer does not care if a bell was already rung (e.g. by the player).
                break;
            }
        }
        this.nextBell = nextBell;
    }

    public void UpdatePhase1() {
        // Charging direction is immediate, but still respects delay frames.
        if (this.charging == Direction.None && this.ringBell == Direction.None) this.charging = this.CanSeePlayer(range: 7);

        if (this.delay > 0) {
            this.delay--;
            return;
        }

        if (this.charging != Direction.None) {
            this.dir = this.charging; // Just for clarity / testing purposes, charging is still the source of truth.
            (var newX, var newY) = this.charging.Add(this.x, this.y);
            if (Global.IsOob(newX, newY)) {
                this.charging = Direction.None; // Charge finished. Stun for 1 frame then we'll resume next frame.
                this.delay = 1;
                return;
            } else if (Global.OccupiedByEnemy(newX, newY, out Enemy? enemy)) {
                if (enemy is Bell bell) {
                    Global.oldEnemies.Add(bell); // Dead Ringer destroys bells if he charges them, but does not damage enemies
                    this.PickNextBell();
                }
                this.charging = Direction.None;
                this.delay = 1;
                return;
            }

            this.x = newX;
            this.y = newY;
            return;
        }

        // If we're winding up to ring a bell, follow through
        if (this.ringBell != Direction.None && this.nextBell != null) {
            this.nextBell.OnHit(this.ringBell, 1);
            this.PickNextBell();
            this.ringBell = Direction.None;
            return;
        }

        // If there's still a bell to ring, move diagonally toward the square north of the bell
        if (this.nextBell != null) {
            var newX = this.x;
            if      (this.x < this.nextBell.x - 1) newX = this.x + 1;
            else if (this.x > this.nextBell.x - 1) newX = this.x - 1;
            var newY = this.y;
            if      (this.y < this.nextBell.y) newY = this.y + 1;
            else if (this.y > this.nextBell.y) newY = this.y - 1;

            // TODO: I'm not sure exactly how Dead Ringer handles situations where the diagonal is blocked. This is fine for now.
            if (Global.OccupiedByEnemy(newX, newY, out _)) newY = this.y;

            this.x = newX;
            this.y = newY;
            this.delay = 1;
            if (this.x == this.nextBell.x - 1 && this.y == this.nextBell.y) {
                this.delay++; // Add an extra delay to simulate the windup
                this.ringBell = Direction.South;
            }
        }
    }

    public Direction dash;
    public void UpdatePhase2() {
        // In phase 2, dead ringer will move diagonally toward the player, then ready and dash at them. This dash is full screen.
        if (this.delay > 0) {
            this.delay--;
            return;
        }

        int newX, newY;
        if (this.dash != Direction.None) {
            bool hitAnything = false;
            while (!hitAnything) {
                (newX, newY) = this.dash.Add(this.x, this.y);
                if (Global.IsOob(newX, newY)) {
                    if (newX == -1 && newY == 5) { // We hit the gong, end the fight
                        Global.oldEnemies.AddRange(Global.enemies);
                    }
                    hitAnything = true;
                } else if (Global.OccupiedByEnemy(newX, newY, out Enemy? enemy)) {
                    enemy.OnHit(this.dash, 8);
                    hitAnything = true;
                } else if (Global.OccupiedByPlayer(newX, newY)) {
                    Player.OnHit(this.dash, 8);
                    hitAnything = true;
                }
                
                if (!hitAnything) {
                    this.x = newX;
                    this.y = newY;
                }
            }

            this.dash = Direction.None;
            return;
        }

        if (this.dash == Direction.None) this.dash = this.CanSeePlayer(6);
        if (this.dash == Direction.None) this.dash = this.CanSeePreviousPlayerPosition(6);
        if (this.dash != Direction.None) return; // This beat is our delayed beat -- we dash on the next beat.

        // Move diagonally toward the player.
        newX = this.x;
        if      (this.x < Player.x) newX++;
        else if (this.x > Player.x) newX--;
        newY = this.y;
        if      (this.y < Player.y) newY++;
        else if (this.y > Player.y) newY--;

        // TODO: I'm not sure exactly how Dead Ringer handles situations where the diagonal is blocked. This is fine for now.
        if (Global.OccupiedByEnemy(newX, newY, out _)) newY = this.y;
        if (Global.OccupiedByPlayer(newX, newY)) {
            Player.OnHit(Direction.None, 4); // TODO: Diagonal damage sources?
            return;
        }

        this.x = newX;
        this.y = newY;
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
            Global.newEnemies.Add(this.enemy);
            this.enemy.Update();
        }
        this.delay = 8;
    }
}

public class Bell : Enemy {
    public bool rung => this.rungOn != -1;
    private int rungOn = -1;
    Func<int, int, Enemy> summon;
    Enemy? enemy;

    public Bell(int x, int y, Func<int, int, Enemy> summon) : base(x, y, 999, 0) {
        this.x = x;
        this.y = y;
        this.summon = summon;
    }

    public override void OnHit(Direction dir, int damage) {
        // Within 9 beats of the last time rung OR miniboss is still alive
        if (this.rung && Global.beat - this.rungOn < 9) return;
        if (this.enemy != null) return;
        this.rungOn = Global.beat;

        (int, int)[] spawnTargets = [(this.x + 1, this.y), (this.x, this.y - 1), (this.x, this.y + 1)];
        foreach ((int x, int y) in spawnTargets) {
            if (Global.OccupiedByPlayer(x, y) || Global.OccupiedByEnemy(x, y, out _)) continue;
            this.enemy = this.summon(x, y);
            this.enemy.Update();
            Global.newEnemies.Add(this.enemy);
            break;
        }

        if (this.enemy == null) {
            (int x, int y) = Global.RandomLocation();
            this.enemy = this.summon(x, y);
        }
    }
}
