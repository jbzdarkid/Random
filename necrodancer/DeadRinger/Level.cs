using System.Collections;
using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Text;

namespace DeadRinger;

public class Level {
    public static Level GlobalLevel;

    public readonly string name;
    public readonly int width;
    public readonly int height;
    public Enemy?[,] grid;

    public Level(string name, int width, int height) {
        this.name = name;
        this.width = width;
        this.height = height;
        this.grid = new Enemy[this.height, this.width];
        GlobalLevel = this;
    }

    public List<Enemy> enemies = [];
    public List<Enemy> newEnemies = []; // A separate list of enemies spawned during this beat, to be added after enemies are updated.
    public List<Enemy> oldEnemies = []; // A separate list of enemies removed during this beat, to be deleted after enemies are updated.
    public int beat = 0;

    public virtual bool IsOob(int x, int y) => y < 0 || y >= this.width || x < 0 || x >= this.height;
    public bool OccupiedByEnemy(int x, int y, [NotNullWhen(returnValue: true)] out Enemy? enemy) => this.OccupiedByEnemy<Enemy>(x, y, out enemy);
    public bool OccupiedByEnemy<T>(int x, int y, [NotNullWhen(returnValue: true)] out T? enemy) where T : Enemy {
        if (x < 0 || x >= this.height) { enemy = null; return false; } // safety check bc IsOob may be overwritten.
        enemy = this.grid[x, y] as T;
        return enemy != null;
    }
    public bool OccupiedByPlayer(int x, int y) => x == Player.x && y == Player.y;

    public (int, int) RandomLocation() {
        return (1, 1); // TODO. Should RNG live inside this class, too?
    }
    
    public State GetState() {
        State state = new();
        state.beat = this.beat;
        state.playerX = Player.x;
        state.playerY = Player.y;
        state.playerPreviousX = Player.previousX;
        state.playerPreviousY = Player.previousY;
        foreach (Enemy enemy in this.enemies) {
            state.enemies.Add(enemy.Clone());
        }
        
        return state;
    }

    public void SetState(State state) {
        this.beat = state.beat;
        Player.x = state.playerX;
        Player.y = state.playerY;
        Player.previousX = state.playerPreviousX;
        Player.previousY = state.playerPreviousY;
        this.enemies.Clear();
        foreach (Enemy enemy in state.enemies) {
            this.enemies.Add(enemy.Clone());
        }
    }

    public virtual bool Won() => throw new NotImplementedException();

    // return value ignored
    public bool Move(Direction dir) {
        Player.previousX = Player.x;
        Player.previousY = Player.y;
        if (dir != Direction.None) {
            int newX = Player.x, newY = Player.y;
            DirectionExtensions.Add(dir, ref newX, ref newY);
            if (this.IsOob(newX, newY)) { } // Player does not move but actions still run
            else if (this.OccupiedByEnemy(newX, newY, out Enemy? enemy)) enemy.OnHit(dir, Player.weaponDamage); // Player does not move because they attacked
            else {
                Player.x = newX;
                Player.y = newY;
            }
        } // Continue running logic for enemies in all cases.

        if (this.name == "Dead Ringer" && Player.x == 10) return true;

        foreach (var enemy in this.enemies) enemy.Update();

        // TODO: Enemy priority goes here, use SortedList.
        this.enemies.RemoveAll(this.oldEnemies.Contains);
        this.enemies.AddRange(this.newEnemies);
        this.newEnemies.Clear();
        this.oldEnemies.Clear();
        this.beat++;

        return true;
    }

    public void InteractiveSolver() {
        while (this.enemies.Count > 0) {
            this.DrawGrid();

            Console.Write($"Beat: {this.beat}, Input: ");
            ConsoleKeyInfo input = Console.ReadKey();
            Console.Write("\n"); // newline after the input is read successfully

            bool Special(string action) {
                Player.Special(action);
                this.Move(Direction.None);
                return true;
            }
            bool validInput = input.Key switch {
                ConsoleKey.E => this.Move(Direction.North),
                ConsoleKey.S => this.Move(Direction.West),
                ConsoleKey.D => this.Move(Direction.South),
                ConsoleKey.F => this.Move(Direction.East),
                ConsoleKey.Spacebar => this.Move(Direction.None),
                ConsoleKey.Q => Special("bomb"),
                ConsoleKey.A => Special("drum"),
                ConsoleKey.W => Special("earth"),
                _ => false,
            };
            if (!validInput) continue;
        }
    }

    public void DrawGrid() {
        StringBuilder output = new();
        // Top wall
        if (Player.x == -1) {
            output.Append("+----");
            for (int y = 4; y < 7; y++) {
                if (this.OccupiedByPlayer(-1, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("----+\n");
        } else {
            output.Append("+" + new string('-', this.width) + "+\n");
        }
        
        // Middle
        for (int x = 0; x < this.height; x++) {
            output.Append('|');
            for (int y = 0; y < this.width; y++) {
                if (this.OccupiedByEnemy(x, y, out Enemy? enemy)) {
                    if (enemy is Bell bell) output.Append(bell.rung ? 'B' : 'b');
                    else if (enemy is DeadRinger deadRinger) output.Append(deadRinger.phase2 ? 'D' : 'd');
                    else output.Append(char.ToLowerInvariant(enemy.GetType().Name?[0] ?? '?'));
                }
                else if (this.OccupiedByPlayer(x, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("|\n");
        }

        // Bottom wall
        if (Player.x == this.height) {
            output.Append("+----");
            for (int y = 4; y < 7; y++) {
                if (this.OccupiedByPlayer(this.height, y)) output.Append('P');
                else output.Append(' ');
            }
            output.Append("----+\n");
        } else {
            output.Append("+" + new string('-', this.width) + "+\n");
        }

        Console.Write(output.ToString());
        Debug.WriteLine(output.ToString());
    }
}

public class DeadRingerFight : Level {
    public DeadRingerFight(int? forcedRng = null) : base("Dead Ringer", 11, 10) {
        this.enemies.Add(new Bell(3, 2, (x, y) => new GreenDragon(x, y, delay: 0)));
        this.enemies.Add(new Bell(3, 8, (x, y) => new Ogre       (x, y, delay: 0)));
        this.enemies.Add(new Bell(8, 2, (x, y) => new Nightmare  (x, y, delay: 0)));
        this.enemies.Add(new Bell(8, 8, (x, y) => new Minotaur   (x, y, delay: 0)));
        int rng = forcedRng ?? RNG.Get(2);
        if (rng == 0) {
            this.enemies.Add(new DeadRinger(4, 3, (Bell)this.enemies[0]));
        } else {
            this.enemies.Add(new DeadRinger(4, 7, (Bell)this.enemies[1]));
        }

        Player.Init(10, 5);
    }

    // Dead ringer is dead and the player is standing where the bell was (where the gold pile is now)
    public override bool Won() => this.enemies.Count == 0 && Player.x == -1 && Player.y == 5;

    public override bool IsOob(int x, int y) {
        // Left and right walls always OOB
        if (y < 0 || y >= this.width) return true;
        // If the player is still in the entryway then 3 tiles are open
        if (Player.x == this.height) return x == this.height && (y < 4 || y > 6);
        // Space around the bell
        if (x == -1) {
            if (this.enemies.Count == 0) return (y < 3 || y > 7); // If dead ringer is dead, 5 tiles are open
            // Else, only allow movement into 4 and 6 (sides of the bell)
            return !(y == 4 || y == 6);
        }

        // all other X values invalid        
        return x < 0 || x >= this.height;
    }
}