package main

import "fmt"
import "sort"

// Maybe just list<solution> and include loc in the soln object?
var solutions = make([]soln_flat, 0);

func main() {
  var e1_pieces = make([]*piece, 8);
  e1_pieces[0] = new_piece('S', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[1] = new_piece('O', loc{3, 0, EAST},   loc{2, 2, EAST});
  e1_pieces[2] = new_piece('L', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[3] = new_piece('O', loc{2, 0, EAST},   loc{3, 2, EAST});
  e1_pieces[4] = new_piece('S', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[5] = new_piece('L', loc{3, 1, WEST},   loc{1, -1, WEST});
  e1_pieces[6] = new_piece('L', loc{3, 1, WEST},   loc{0, 0, NORTH});
  e1_pieces[7] = new_piece('L', loc{3, 1, NORTH},  loc{1, 1, EAST});

  solve_bridge(e1_pieces[0:3], loc{-1, 0, NORTH}, loc{-9, -1, NORTH}); // 8 units forward, 1 unit left.
}

func solve_bridge(pieces []*piece, enter loc, exit loc) {
  // Large to have scratch space.
  grid := make([][]int, 100);
  for x := range(grid) { grid[x] = make([]int, 100); }
  grid[50][50] = 1; // Always the enter point (so 0,0 == 50,50)
  grid[50 + exit.x][50 + exit.y] = 1;

  fmt.Println("Building a bridge with these pieces:");
  for _, p := range pieces {
    p.print();
  }

  solve_bridge_recursive(
    grid,
    pieces,
    loc{enter.x+50, enter.y+50, enter.ori}, // position
    soln{}, // solution buffer
  );

  sort.Slice(solutions, func(i int, j int) bool {
    if solutions[i].exit.x < solutions[j].exit.x { return true; }
    if solutions[i].exit.x > solutions[j].exit.x { return false; }

    if solutions[i].exit.y < solutions[j].exit.y { return true; }
    if solutions[i].exit.y > solutions[j].exit.y { return false; }

    return false;
  });

  for i, s := range solutions {
    fmt.Printf("Solution %d reached location (%d, %d) with pattern: %s\n", i, s.exit.x, s.exit.y, s.name);
  }
}

func solve_bridge_recursive(grid [][]int, pieces []*piece, position loc, s soln) {
  for i, p := range pieces {
    if p.shape == rune(0) { continue; }

    for flip := 0; flip < 2; flip++ {
      // First, try placing the piece normally.
      {
        q, name := p.transform(position, flip == 1, nil);
        // If this piece does not fit on the grid, then flipswaps won't work either.
        if !q.can_place(grid) { continue; }

        q.place(grid, +1);
        s.push(name);
        pieces[i].shape = rune(0); // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, s);
        pieces[i].shape = q.shape;
        s.pop();
        q.place(grid, -1);
      }

      // Given that the piece was placable, we can try running a flipswap.
      prev_i := -1
      next_i := -1
      for j := 1; j < len(pieces); j++ {
        k := (i + j) % len(pieces);
        if pieces[k].shape != rune(0) { prev_i = k; }
        k = (i - j + len(pieces)) % len(pieces);
        if pieces[k].shape != rune(0) { next_i = k; }
      }
      fmt.Printf("Computed adjacent pieces. i=%d, prev_i=%d, next_i=%d\n", i, prev_i, next_i);

      // Flipswap backwards (i.e. target = previous piece)
      if prev_i != -1 {
        q, name := pieces[prev_i].transform(position, flip == 1, p);
        // Flipswaps don't care about target placement safety.

        q.place(grid, +1);
        s.push(name);
        pieces[prev_i].shape = rune(0); // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, s);
        pieces[prev_i].shape = q.shape;
        s.pop();
        q.place(grid, -1);
      }

      // Flipswap forwards (i.e. target = next piece)
      if prev_i != next_i {
        q, name := pieces[next_i].transform(position, flip == 1, p);
        // Flipswaps don't care about target placement safety.

        q.place(grid, +1);
        s.push(name);
        pieces[next_i].shape = rune(0); // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, s);
        pieces[next_i].shape = q.shape;
        s.pop();
        q.place(grid, -1);
      }
    }
  }

  solutions = append(solutions, s.flatten(position));
}

type soln struct {
  data  [100]string;
  count int;
  cost  int;
}

func (s *soln) push (val string) {
  s.data[s.count] = val;
  s.count++;
}

func (s *soln) pop () string {
  if s.count == 0 { return ""; }
  s.count--;
  return s.data[s.count];
}

type soln_flat struct {
  name string;
  exit loc;
  cost int;
}

func (s *soln) flatten (exit loc) soln_flat {
  sf := soln_flat{"", exit, s.cost};
  for i := 0; i < s.count; i++ {
    if len(sf.name) != 0 { sf.name += ", "; }
    sf.name += s.data[i];
  }
  return sf;
}

const NORTH = 0;
const EAST  = 1;
const SOUTH = 2;
const WEST  = 3;
type loc struct { x int; y int; ori int; }

type piece struct {
  shape rune;
  enter loc;
  exit  loc;
  cells [4]loc;
};

func new_piece(shape rune, enter loc, exit loc) *piece {
  p := new(piece);
  p.shape = shape;
  p.enter = enter;
  p.exit  = exit;

  switch p.shape {
  case 'I':
    p.cells = [4]loc{loc{0, 0, 0}, loc{1, 0, 0}, loc{2, 0, 0}, loc{3, 0, 0}};
  case 'L':
    p.cells = [4]loc{loc{1, 0, 0}, loc{2, 0, 0}, loc{3, 0, 0}, loc{3, 1, 0}};
  case 'S':
    p.cells = [4]loc{loc{1, 0, 0}, loc{2, 0, 0}, loc{2, 1, 0}, loc{3, 1, 0}};
  case 'O':
    p.cells = [4]loc{loc{2, 0, 0}, loc{2, 1, 0}, loc{3, 0, 0}, loc{3, 1, 0}};
  case 'T':
    p.cells = [4]loc{loc{2, 0, 0}, loc{2, 1, 0}, loc{2, 2, 0}, loc{3, 1, 0}};
  }

  return p;
}

func (p *piece) contains (x int, y int) bool {
  for _, c := range p.cells {
    if c.x == x && c.y == y { return true; }
  }
  return false;
}

func (p *piece) print() {
  output := "";
  for x := -1; x < 5; x++ {
    for y := -1; y < 5; y++ {
      // For no apparently good reason, you need to have the '} else' together or else go inserts a semicolon for you.
      // ALSO you need parenthesis around the conditions here. Something about the inline loc{} declaration, I guess.
      if (p.contains(x, y)) {
        if (p.enter == loc{x, y, NORTH})   { output += "^"; } else
        if (p.enter == loc{x, y, SOUTH})   { output += "v"; } else
        if (p.enter == loc{x, y, WEST})    { output += "<"; } else
        if (p.enter == loc{x, y, EAST})    { output += ">"; } else
        if (p.exit  == loc{x-1, y, NORTH}) { output += "^"; } else
        if (p.exit  == loc{x+1, y, SOUTH}) { output += "v"; } else
        if (p.exit  == loc{x, y-1, WEST})  { output += "<"; } else
        if (p.exit  == loc{x, y+1, EAST})  { output += ">"; } else
                                           { output += "#"; }
      } else {
        x_edge := (x == -1 || x == 4);
        y_edge := (y == -1 || y == 4);
        if (x_edge && y_edge)              { output += "+"; } else
        if (x_edge && !y_edge)             { output += "-"; } else
        if (!x_edge && y_edge)             { output += "|"; } else
        if (!x_edge && !y_edge)            { output += " "; }
      }
    }
    output += "\n";
  }
  fmt.Print(output);
}

// rotation: Integer, number of 90 degree clockwise rotations.
func (p *piece) rotate(rotation int) {
  rotation = ((rotation % 4) + 4) % 4;
  for i := 0; i < rotation; i++ {
    p.enter = loc{p.enter.y, 3 - p.enter.x, (p.enter.ori + 1) % 4};
    p.exit  = loc{p.exit.y,  3 - p.exit.x,  (p.exit.ori + 1) % 4};
    for i, cell := range p.cells {
      p.cells[i] = loc{cell.y, 3 - cell.x, cell.ori};
    }
  }
}

func (p *piece) flip() {
  p.enter = loc{p.enter.x, 3 - p.enter.y, (4 - p.enter.ori) % 4};
  p.exit  = loc{p.exit.x,  3 - p.exit.y,  (4 - p.exit.ori) % 4};
  for i, cell := range p.cells {
    p.cells[i] = loc{cell.x, 3 - cell.y, cell.ori};
  }
}

func (p *piece) translate(x int, y int) {
  p.enter = loc{p.enter.x + x, p.enter.y + y, p.enter.ori};
  p.exit  = loc{p.exit.x + x,  p.exit.y + y,  p.exit.ori};
  for i, cell := range p.cells {
    p.cells[i] = loc{cell.x + x, cell.y + y, cell.ori};
  }
}

/**
 * Rotate, translate, flip, or flipswap a piece (before placing it)
 * target: Loc, target position and orientiation (within the larger grid).
 * flip: Boolean, if the piece is flipped (or the source piece is flipped, if nonnil
 * source: &Piece, the flipswap source piece. See this video for an explanation.
 *   https://youtu.be/OLKT43q9EYY
 *   Optional value indicated by nil, in which case no flipswap is applied.
**/
func (p *piece) transform(position loc, flip bool, source *piece) (*piece, string) {
  q := new_piece(p.shape, p.enter, p.exit); // Copy and we'll just modify the copy

  if source == nil { // Normal, non-flipswap behavior.
    q.rotate(position.ori - q.enter.ori);
    if flip { q.flip(); }
    q.translate(3 - q.enter.x, 0 - q.enter.y);

  } else { // Buggy flipswap behavior
    fmt.Println("flipswapping, source piece:");
    r := new_piece(source.shape, source.enter, source.exit);
    r.print();

    fmt.Println("Target piece:");
    q.print();
    // Green: "Safety" adjustment for S and T (pieces with a hole at (3, 0))
    fmt.Println("green -- shifting source piece");
    r.print();
    if r.shape == 'T' || r.shape == 'S' { r.translate(0, -1); }

    // Red: Apply normal rotation and flip computation for the source piece
    fmt.Println("red -- rotating and flipping source piece");
    r.rotate(position.ori - source.enter.ori);
    r.print();
    if flip { r.flip(); r.print(); }

    // Blue: Apply the source rotation and flip to the target piece, then adjust based on the source's entrance
    fmt.Println("blue -- adjusting target based on source adjustment. Initial:");
    q.print();
    q.rotate(position.ori - source.enter.ori);
    fmt.Println("rotated");
    q.print();
    if flip { q.flip(); fmt.Println("flipped"); q.print(); }
    fmt.Printf("Translating by %s\n", r.enter);
    q.translate(3 - r.enter.x, 0 - r.enter.y);
    q.print();
  }

  q.translate(position.x - 3, position.y - 0); // We are using 3,0 as our entry point (since it makes the pictures look nice.)

  var name string;
  if source != nil && flip  { name = fmt.Sprintf("(%c'%c)", source.shape, p.shape); }
  if source != nil && !flip { name = fmt.Sprintf("(%c%c)", source.shape, p.shape); }
  if source == nil && flip  { name = fmt.Sprintf("%c'", p.shape); }
  if source == nil && !flip { name = fmt.Sprintf("%c", p.shape); }

  return q, name;
}

func print_grid(grid [][]int, error loc) {
  grid_bounds := []int{0, 0, 100, 100};
  for x := 0; x < len(grid); x++ {
    row_clear := true
    for y := 0; y < len(grid[x]); y++ {
      if grid[x][y] > 0 { row_clear = false; break; }
    }
    if !row_clear { break; }
    grid_bounds[0] = x;
  }
  for x := len(grid) - 1; x >= 0; x-- {
    row_clear := true
    for y := 0; y < len(grid[x]); y++ {
      if grid[x][y] > 0 { row_clear = false; break; }
    }
    if !row_clear { break; }
    grid_bounds[1] = x;
  }
  for y := 0; y < len(grid[0]); y++ {
    col_clear := true
    for x := 0; x < len(grid); x++ {
      if grid[x][y] > 0 { col_clear = false; break; }
    }
    if !col_clear { break; }
    grid_bounds[2] = y;
  }
  for y := len(grid[0]) - 1; y >= 0; y-- {
    col_clear := true
    for x := 0; x < len(grid); x++ {
      if grid[x][y] > 0 { col_clear = false; break; }
    }
    if !col_clear { break; }
    grid_bounds[3] = y;
  }

  output := "+";
  for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
    output += "-";
  }
  output += "+\n";
  for x := grid_bounds[0]; x < grid_bounds[1]; x++ {
    output += "|";
    for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
      if (x == 50 && y == 50)           { output += "S"; } else
      if (x == error.x && y == error.y) { output += "*"; } else
      if grid[x][y] == 0                { output += " "; } else
                                        { output += fmt.Sprintf("%d", grid[x][y]); }
    }
    output += "|\n";
  }
  output += "+";
  for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
    output += "-";
  }
  output += "+\n";
  fmt.Print(output);
}

func (p *piece) can_place(grid [][]int) bool {
  for _, c := range p.cells {
    if grid[c.x][c.y] > 0 {
      fmt.Printf("Attempted to place piece %c but it collided with the grid at (%d, %d)\n", p.shape, c.x, c.y);
      print_grid(grid, c);

      return false; // Collides with existing piece
    }
  }

  return true;
}

func (p *piece) place(grid [][]int, delta int) {
  for _, c := range p.cells {
    grid[c.x][c.y] += delta;
  }
}


