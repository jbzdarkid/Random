namespace DeadRinger;

public static class Program {
    public static void Main() {
        RNG.Seed(0);
        Level level = new DeadRingerFight();
        // level.InteractiveSolver();
        new Solver(level).Solve();
    }
}