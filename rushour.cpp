#include <stdio.h>
#include <string.h>
#include <stdint.h>

struct puzzle {
    uint64_t vehicles[32];
    char     names[32];
    uint64_t blocked;
    uint64_t escape;
    uint32_t direction;
    int16_t  nvehicles;
    int16_t  escape_vehicle;
};

static void
puzzle_load(struct puzzle *p)
{
    /* Clear some fields. */
    p->blocked = 0;
    p->nvehicles = 0;
    p->direction = 0;
    p->escape = 0;
    p->escape_vehicle = -1;

    /* Load entire input. */
    char buffer[9][9] = {{0}};
    for (int i = 0; i < 8; i++)
        fgets(buffer[i], sizeof(buffer[i]), stdin);

    /* Scan for vehicles. */
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            char c = buffer[y][x];
            if (c >= 'A' && c <= 'Z') {
                int i = p->nvehicles++;
                p->names[i] = c;
                if (c == 'R')
                    p->escape_vehicle = i;
                p->vehicles[i] = UINT64_C(1) << (y * 8 + x);
                for (int d = 1; buffer[y + d][x] == c; d++) {
                    p->direction |= UINT64_C(1) << i;
                    buffer[y + d][x] = '.';
                    p->vehicles[i] |= UINT64_C(1) << ((y + d) * 8 + x);
                }
                for (int d = 1; buffer[y][x + d] == c; d++) {
                    buffer[y][x + d] = '.';
                    p->vehicles[i] |= UINT64_C(1) << (y * 8 + (x + d));
                }
            } else if (c == '>') {
                p->escape |= UINT64_C(1) << (y * 8 + x);
            } else if (c != '.') {
                p->blocked |= UINT64_C(1) << (y * 8 + x);
            }
        }
    }
}

/* Returns the mask for coverage of all vehicles. */
static uint64_t
puzzle_full_blocked(const struct puzzle *p)
{
    uint64_t mask = p->blocked;
    for (int i = 0; i < p->nvehicles; i++)
        mask |= p->vehicles[i];
    return mask;
}

#define EDGE_TOP     UINT64_C(0xff00000000000000)
#define EDGE_BOTTOM  UINT64_C(0x00000000000000ff)
#define EDGE_RIGHT   UINT64_C(0x0101010101010101)
#define EDGE_LEFT    UINT64_C(0x8080808080808080)

/* Compute the range of motion for vehicle i. */
static void
puzzle_options(struct puzzle *p, int i, int *min, int *max, uint64_t blocked)
{
    int dir = (p->direction >> i) & 1;
    int delta = dir ? 8 : 1;
    uint64_t min_wall = dir ? EDGE_BOTTOM : EDGE_RIGHT;
    uint64_t max_wall = dir ? EDGE_TOP    : EDGE_LEFT;
    uint64_t vehicle = p->vehicles[i];
    uint64_t mask = blocked & ~vehicle; // remove this vehicle
    for (*min = 0; ; (*min)++) {
        if ((vehicle >> (*min * delta)) & mask) {
            /* Ran into another vehicle. */
            (*min)--;
            break;
        } else if ((vehicle >> (*min * delta)) & min_wall) {
            /* Ran into the edge. */
            break;
        }
    }
    for (*max = 0; ; (*max)++) {
        if ((vehicle << (*max * delta)) & mask) {
            /* Ran into another vehicle. */
            (*max)--;
            break;
        } else if ((vehicle << (*max * delta)) & max_wall) {
            /* Ran into the edge. */
            break;
        }
    }
}

struct move {
    int16_t vehicle;
    int8_t how;
};

static int
solve(struct puzzle *p,
      struct move *solution,  // place to store the best solution
      int best,               // solution size
      struct move *workspace, // partial candidate solution
      int n)                  // number of elements in workspace
{
    if (n == best)
        return best; // workspace too long

    uint64_t blocked = puzzle_full_blocked(p);
    for (int i = 0; i < p->nvehicles; i++) {
        if (n > 0 && workspace[n - 1].vehicle == i)
            continue; // don't move same vehicle twice in a row
        workspace[n].vehicle = i;
        uint64_t original = p->vehicles[i];
        int dir = (p->direction >> i) & 1;
        int delta = dir ? 8 : 1;

        int min, max;
        puzzle_options(p, i, &min, &max, blocked);
        for (int d = -min; d <= max; d++) {
            if (d == 0)
                continue; // don't do nothing
            workspace[n].how = d;
            uint64_t vehicle;
            if (d < 0)
                vehicle = original >> (-d * delta);
            else
                vehicle = original << (+d * delta);

            if (p->escape_vehicle == i && vehicle & p->escape) {
                /* Found a solution. */
                memcpy(solution, workspace, (n + 1) * sizeof(*solution));
                return n + 1;
            } else {
                /* Keep looking. */
                p->vehicles[i] = vehicle;
                best = solve(p, solution, best, workspace, n + 1);
                p->vehicles[i] = original;
            }
        }
    }
    return best;
}

int
main(void)
{
    struct puzzle puzzle;
    puzzle_load(&puzzle);
    struct move workspace[12];
    struct move solution[12];
    int max = sizeof(solution) / sizeof(*solution);
    int n = solve(&puzzle, solution, max, workspace, 0);
    if (n == max)
        printf("No solution.\n");
    else {
        for (int i = 0; i < n; i++) {
            char name = puzzle.names[solution[i].vehicle];
            printf("%c %+d\n", name, solution[i].how);
        }
    }
    return 0;
}