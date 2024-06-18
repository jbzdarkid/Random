namespace DeadRinger;

public static class Program {
    public static Level InitDeadRinger() {
        Level level = new("Dead Ringer", 11, 10);
        level.enemies.Add(new Bell(3, 2, (x, y) => new GreenDragon(x, y, delay: 0)));
        level.enemies.Add(new Bell(3, 8, (x, y) => new Ogre       (x, y, delay: 0)));
        level.enemies.Add(new Bell(8, 2, (x, y) => new Nightmare  (x, y, delay: 0)));
        level.enemies.Add(new Bell(8, 8, (x, y) => new Minotaur   (x, y, delay: 0)));
        if (RNG.Get(2) == 0) {
            level.enemies.Add(new DeadRinger(4, 3, (Bell)level.enemies[0]));
        } else {
            level.enemies.Add(new DeadRinger(4, 7, (Bell)level.enemies[1]));
        }

        Player.Init(10, 5);

        return level;
    }

    public static void Main() {
        Level level = InitDeadRinger();
        RNG.Seed(0);
        level.InteractiveSolver();
    }
}