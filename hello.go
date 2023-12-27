package main

import "fmt"
import "sort"

var solutions = make([]soln_flat, 0);

func main() {
  var e1_pieces [8]*piece;
  e1_pieces[0] = new_piece('S', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[1] = new_piece('O', loc{3, 0, EAST},   loc{2, 2, EAST});
  e1_pieces[2] = new_piece('L', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[3] = new_piece('O', loc{2, 0, EAST},   loc{3, 2, EAST});
  e1_pieces[4] = new_piece('S', loc{3, 1, NORTH},  loc{0, 0, NORTH});
  e1_pieces[5] = new_piece('L', loc{3, 1, WEST},   loc{1, -1, WEST});
  e1_pieces[6] = new_piece('L', loc{3, 1, WEST},   loc{0, 0, NORTH});
  e1_pieces[7] = new_piece('L', loc{3, 1, NORTH},  loc{1, 1, EAST});
  // solve_bridge(e1_pieces[0:3], NORTH, loc{-8, -1, NORTH});
  // solve_bridge(e1_pieces[3:6], NORTH, loc{-7, 2, NORTH});
  // solve_bridge(e1_pieces[6:8], NORTH, loc{-5, -1, NORTH});

  var e2_pieces [8]*piece;
  e2_pieces[0] = new_piece('I', loc{3, 0, WEST},  loc{-1, 0, NORTH});
  e2_pieces[1] = new_piece('T', loc{3, 1, NORTH}, loc{1, 2, NORTH});
  e2_pieces[2] = new_piece('S', loc{3, 1, NORTH}, loc{-1, 1, WEST});
  e2_pieces[3] = new_piece('L', loc{3, 1, NORTH}, loc{0, 0, NORTH});
  e2_pieces[4] = new_piece('I', loc{3, 0, NORTH}, loc{0, 1, EAST});
  e2_pieces[5] = new_piece('O', loc{3, 0, EAST},  loc{1, 1, NORTH});
  e2_pieces[6] = new_piece('L', loc{3, 1, WEST},  loc{1, -1, WEST});
  e2_pieces[7] = new_piece('T', loc{2, 2, WEST},  loc{2, -1, WEST});
  // solve_bridge(e2_pieces[0:4], NORTH, loc{-8, 0, NORTH});
  // solve_bridge(e2_pieces[4:8], NORTH, loc{-10, 0, NORTH});
  
  var n2_pieces [8]*piece;
  n2_pieces[0] = new_piece('S', loc{3, 1, NORTH}, loc{0, 0, NORTH});
  n2_pieces[1] = new_piece('S', loc{3, 1, NORTH}, loc{0, 0, NORTH});
  n2_pieces[2] = new_piece('L', loc{3, 1, NORTH}, loc{0, 0, NORTH});
  n2_pieces[3] = new_piece('I', loc{3, 0, WEST},  loc{0, -1, WEST});
  n2_pieces[4] = new_piece('S', loc{3, 1, NORTH}, loc{0, 0, NORTH});
  n2_pieces[5] = new_piece('T', loc{3, 1, NORTH}, loc{2, -1, WEST});
  n2_pieces[6] = new_piece('S', loc{3, 1, NORTH}, loc{1, -1, WEST});
  n2_pieces[7] = new_piece('L', loc{3, 1, WEST},  loc{1, -1, WEST});
  // solve_bridge(n2_pieces[0:3], NORTH, loc{-10, 0, NORTH});
  solve_bridge(n2_pieces[4:7], NORTH, loc{-9, 0, NORTH});

  // s3_pieces = {
  // }
  // w2_pieces = {
  // }
  
}

func solve_bridge(pieces []*piece, enter_ori int, exit loc) {
  // Large to have scratch space.
  grid := make([][]int, 100);
  for x := range(grid) { grid[x] = make([]int, 100); }
  grid[51][50] = 1; // The first piece is always at 50,50

  print("Building a bridge with these pieces:");
  for _, p := range pieces {
    p.print();
  }

  solve_bridge_recursive(
    grid,
    pieces,
    loc{50, 50, enter_ori}, // position
    loc{exit.x+50, exit.y+50, exit.ori}, // exit
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

func solve_bridge_recursive(grid [][]int, pieces []*piece, position loc, exit loc, s soln) {
  for i, p := range pieces {
    if p.shape == rune(0) { continue; } // Signal value, piece has already been placed

    for _, flip := range ([]bool {false, true}) {
      // First, try placing the piece normally.
      {
        q := p.transform(position, flip, nil);
        // If this piece does not fit on the grid, then flipswaps won't work either.
        if !q.can_place(grid) { continue; }

        s.add_piece(p, i, flip, nil, grid);
        q.place(grid, +1);
        pieces[i].shape = rune(0); // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, exit, s);
        pieces[i].shape = q.shape;
        q.place(grid, -1);
        s.pop_piece();
      }

      // Given that the piece was placable, we can try running a flipswap.
      var prev_piece *piece;
      var next_piece *piece;
      for j := 1; j < len(pieces); j++ {
        k := (i + j) % len(pieces);
        if pieces[k].shape != rune(0) { prev_piece = pieces[k]; }
        k = (i - j + len(pieces)) % len(pieces);
        if pieces[k].shape != rune(0) { next_piece = pieces[k]; }
      }

      // Flipswap backwards (i.e. target = previous piece)
      if prev_piece != nil {
        q := prev_piece.transform(position, flip, p);
        // Flipswaps don't care about target placement safety.
        // However, we do care that the pathway is still walkable.
        if !q.can_walk(grid) { continue; }

        s.add_piece(p, i, flip, q, grid);
        q.place(grid, +1);
        prev_piece.shape = rune(0); // Placeholder to indicate that we have placed this shape
        print_grid(grid, q.exit, nil);
        solve_bridge_recursive(grid, pieces, q.exit, exit, s);
        prev_piece.shape = q.shape;
        q.place(grid, -1);
        s.pop_piece();
      }

      // Flipswap forwards (i.e. target = next piece)
      if prev_piece != next_piece {
        q := next_piece.transform(position, flip, p);
        // Flipswaps don't care about target placement safety.
        // However, we do care that the pathway is still walkable.
        if !q.can_walk(grid) { continue; }

        s.add_piece(p, i, flip, q, grid);
        q.place(grid, +1);
        next_piece.shape = rune(0); // Placeholder to indicate that we have placed this shape
        print_grid(grid, q.exit, nil);
        solve_bridge_recursive(grid, pieces, q.exit, exit, s);
        next_piece.shape = q.shape;
        q.place(grid, -1);
        s.pop_piece();
      }
    }
  }

  sf := s.flatten(position);
  solutions = append(solutions, sf);
  if sf.exit == exit {
    debug = true;
    print(sf.name);
    print_grid(grid, sf.exit, nil);
    debug = false;
  }
}

type soln struct {
  data  [100]string;
  count int;
  cost  int;
}

func (s *soln) add_piece (source *piece, source_i int, flip bool, target *piece, grid [][]int) {
  var name string;
  name += fmt.Sprintf("%c%d", source.shape, source_i);
  if flip { name += "'"; }
  if target != nil {
    name = fmt.Sprintf("(%s-%c)", name, target.shape);

    bridge_is_safe := false;
    switch target.enter.ori {
      case NORTH: bridge_is_safe = grid[target.enter.x + 1][target.enter.y] > 0;
      case SOUTH: bridge_is_safe = grid[target.enter.x - 1][target.enter.y] > 0;
      case EAST:  bridge_is_safe = grid[target.enter.x][target.enter.y + 1] > 0;
      case WEST:  bridge_is_safe = grid[target.enter.x][target.enter.y - 1] > 0;
    }
    if !bridge_is_safe {
      name = "!" + name;
      print_grid(grid, target.enter, target);
    }
  }

  s.data[s.count] = name;
  s.count++;
}

func (s *soln) pop_piece () {
  if s.count > 0 { s.count--; }
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
  print(output);
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
func (p *piece) transform(position loc, flip bool, source *piece) *piece {
  q := new_piece(p.shape, p.enter, p.exit); // Copy and we'll just modify the copy

  if source == nil { // Normal, non-flipswap behavior.
    q.rotate(position.ori - q.enter.ori);
    if flip { q.flip(); }
    q.translate(3 - q.enter.x, 0 - q.enter.y);
  } else { // Buggy flipswap behavior
    print("flipswapping, source piece:");
    r := new_piece(source.shape, source.enter, source.exit);
    r.print();

    print("Target piece:");
    q.print();

    // Green: "Safety" adjustment for S and T (pieces with a hole at (3, 0))
    // TODO: This is probably just a different storage mechanism and I'm being dumb.
    print("green -- shifting source/target piece.")
    if q.shape == 'T' || q.shape == 'S' { q.translate(0, -1); }
    if r.shape == 'T' || r.shape == 'S' { r.translate(0, -1); }

    // Red: Apply normal rotation and flip computation for the source piece
    print("red -- rotating and flipping source piece");
    r.rotate(position.ori - source.enter.ori);
    r.print();
    if flip { r.flip(); r.print(); }

    // Blue: Apply the source transformation to the target piece.
    print("blue -- adjusting target based on source adjustment");
    q.rotate(position.ori - source.enter.ori);
    print("rotated");
    q.print();
    if flip { q.flip(); print("flipped"); q.print(); }
    print("translated");
    q.translate(3 - r.enter.x, 0 - r.enter.y);
    q.print();
  }

  // Translate to grid coords. We are using 3,0 as our entry point since it makes the pictures look nice.
  q.translate(position.x - 3, position.y - 0);

  return q;
}

func print_grid(grid [][]int, error loc, p *piece) {
  grid_bounds := []int{0, 0, 100, 100};
  fudge := 5
  for x := 0; x < len(grid); x++ {
    row_clear := true
    for y := 0; y < len(grid[x]); y++ {
      if grid[x][y] > 0 { row_clear = false; break; }
    }
    if !row_clear { break; }
    grid_bounds[0] = x - fudge;
  }
  for x := len(grid) - 1; x >= 0; x-- {
    row_clear := true
    for y := 0; y < len(grid[x]); y++ {
      if grid[x][y] > 0 { row_clear = false; break; }
    }
    if !row_clear { break; }
    grid_bounds[1] = x + fudge;
  }
  for y := 0; y < len(grid[0]); y++ {
    col_clear := true
    for x := 0; x < len(grid); x++ {
      if grid[x][y] > 0 { col_clear = false; break; }
    }
    if !col_clear { break; }
    grid_bounds[2] = y - fudge;
  }
  for y := len(grid[0]) - 1; y >= 0; y-- {
    col_clear := true
    for x := 0; x < len(grid); x++ {
      if grid[x][y] > 0 { col_clear = false; break; }
    }
    if !col_clear { break; }
    grid_bounds[3] = y + fudge;
  }

  output := "+";
  for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
    output += "-";
  }
  output += "+\n";
  for x := grid_bounds[0]; x < grid_bounds[1]; x++ {
    output += "|";
    for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
      if (x == 51 && y == 50)           { output += "S"; } else
      if (x == error.x && y == error.y) { output += "*"; } else
      if (p != nil && p.contains(x, y)) { output += "X"; } else
      if grid[x][y] == 0                { output += " "; } else
                                        { output += fmt.Sprintf("%d", grid[x][y]); }
    }
    output += "|\n";
  }
  output += "+";
  for y := grid_bounds[2]; y < grid_bounds[3]; y++ {
    output += "-";
  }
  output += "+";
  print(output);
}

var debug bool = false
func print(args ...interface{}) {
  if debug { fmt.Println(args); }
}

func (p *piece) can_place(grid [][]int) bool {
  for _, c := range p.cells {
    if grid[c.x][c.y] > 0 {
      print("Attempted to place a piece but it collided with the grid");
      print_grid(grid, c, p);
      return false;
    }
  }

  return true;
}

func (p *piece) can_walk(grid [][]int) bool {
  walkable := false
  for _, c := range p.cells {
    walkable = walkable || (grid[c.x-1][c.y-1] > 0);
    walkable = walkable || (grid[c.x-1][c.y  ] > 0);
    walkable = walkable || (grid[c.x-1][c.y+1] > 0);
    walkable = walkable || (grid[c.x  ][c.y-1] > 0);
    walkable = walkable || (grid[c.x  ][c.y+1] > 0);
    walkable = walkable || (grid[c.x+1][c.y-1] > 0);
    walkable = walkable || (grid[c.x+1][c.y  ] > 0);
    walkable = walkable || (grid[c.x+1][c.y+1] > 0);
  }

  if !walkable {
    print("Attempted to place a piece but it cannot be walked onto");
    print_grid(grid, p.enter, p);
    return false;
  }

  return true;
}

func (p *piece) place(grid [][]int, delta int) {
  for _, c := range p.cells {
    grid[c.x][c.y] += delta;
  }
}


