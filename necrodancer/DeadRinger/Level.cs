using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Text;

namespace DeadRinger;

public class Level {
    public static Level GlobalLevel;

    public readonly string name;
    public readonly int width;
    public readonly int height;

    public Level(string name, int width, int height) {
        this.name = name;
        this.width = width;
        this.height = height;
        GlobalLevel = this;
    }

    public List<Enemy> enemies = [];
    public List<Enemy> newEnemies = []; // A separate list of enemies spawned during this beat, to be added after enemies are updated.
    public List<Enemy> oldEnemies = []; // A separate list of enemies removed during this beat, to be deleted after enemies are updated.
    public int beat = 0;

    public bool IsOob(int x, int y) {
        if (y < 0 || y >= this.width || x < 0) return true;
        if (Player.x == this.height) return x == this.height && (y < 4 || y > 6);
        return x >= this.height;
    }

    public bool OccupiedByEnemy(int x, int y, [NotNullWhen(returnValue: true)] out Enemy? enemy) => this.OccupiedByEnemy<Enemy>(x, y, out enemy);
    public bool OccupiedByEnemy<T>(int x, int y, [NotNullWhen(returnValue: true)] out T? enemy) where T : Enemy {
        enemy = this.enemies.Find(enemy => enemy.x == x && enemy.y == y) as T;
        return enemy != null;
    }
    public bool OccupiedByPlayer(int x, int y) => x == Player.x && y == Player.y;

    public (int, int) RandomLocation() {
        return (1, 1); // TODO. Should RNG live inside this class, too?
    }
    
    // TODO: Implement these!
    public State GetState() => null;
    public void SetState(State state) { }
    public bool Won() => false;


    public bool Move(Direction dir) {
        Player.previousX = Player.x;
        Player.previousY = Player.y;
        if (dir != Direction.None) {
            (var newX, var newY) = dir.Add(Player.x, Player.y);
            if (this.IsOob(newX, newY)) { } // Player does not move but actions still run
            else if (this.OccupiedByEnemy(newX, newY, out Enemy? enemy)) enemy.OnHit(dir, Player.weaponDamage); // Player does not move because they attacked
            else {
                Player.x = newX;
                Player.y = newY;
            }
        } // Continue running logic for enemies in all cases.

        if (this.name == "Dead Ringer" && Player.x == 10) return true; // Still in the entryway, fight hasn't started yet.

        foreach (var enemy in this.enemies) enemy.Update();

        // TODO: Enemy priority goes here, use SortedList.
        this.enemies.RemoveAll(this.oldEnemies.Contains);
        this.enemies.AddRange(this.newEnemies);
        this.newEnemies.Clear();
        this.oldEnemies.Clear();
        this.beat++;

        return true; // No illegal moves as of yet
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
        StringBuilder output = new("+" + new string('-', this.width) + "+\n");
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