package main

import "fmt"

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

  solve_bridge(e1_pieces[0:3], loc{0, 0, NORTH}, loc{-9, -1, NORTH}); // 8 units forward, 1 unit left.
}

func solve_bridge(pieces []*piece, enter loc, exit loc) {
  // Large to have scratch space.
  grid := make([][]bool, 100);
  for x := range(grid) { grid[x] = make([]bool, 100); }
  grid[50][50] = true; // Always the enter point (so 0,0 == 50,50)
  grid[50 + exit.x][50 + exit.y] = true;

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

  for i, s := range solutions {
    fmt.Printf("Solution %d reached location (%d, %d) with pattern: %s\n", i, s.exit.x, s.exit.y, s.name);
  }
}

func solve_bridge_recursive(grid [][]bool, pieces []*piece, position loc, s soln) {
  for i, p := range pieces {
    if p.shape == rune(0) { continue; }

    var prev_piece *piece;
    var next_piece *piece;
    for j := 0; j < len(pieces); j++ {
      k := (i + j) % len(pieces);
      if pieces[k].shape != rune(0) { prev_piece = pieces[k]; }
      k = (i - j + len(pieces)) % len(pieces);
      if pieces[k].shape != rune(0) { next_piece = pieces[k]; }
    }

    for option := 0; option < 2; option++ {
      flip := (option % 2) == 0;
      flipswap := (option % 6) / 2;
      var source *piece
      if flipswap == 0 { source = nil; }
      if flipswap == 1 { source = prev_piece; }
      if flipswap == 2 { source = next_piece; }

      q, name := p.transform(position, flip, source);
      placed := q.place(grid);
      if placed {
        s.push(name);

        pieces[i].shape = rune(0) // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, s);
        pieces[i].shape = q.shape;

        s.pop();
        q.unplace(grid);
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
    p.exit  = loc{p.exit.y,  3 - p.exit.x, (p.exit.ori + 1) % 4};
    for i, cell := range p.cells {
      p.cells[i] = loc{cell.y, 3 - cell.x, cell.ori};
    }
  }
}

func (p *piece) flip() {
  p.enter = loc{p.enter.x, 3 - p.enter.y, (4 - p.enter.ori) % 4};
  p.exit  = loc{p.exit.x,  3 - p.exit.y, (4 - p.enter.ori) % 4};
  for i, cell := range p.cells {
    p.cells[i] = loc{cell.x, 3 - cell.y, cell.ori};
  }
}

func (p *piece) translate(x int, y int) {
  p.enter = loc{p.enter.x + x, p.enter.y + y, p.enter.ori};
  p.exit  = loc{p.exit.x + x,  p.exit.y + y, p.enter.ori};
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
    fmt.Printf("Transforming piece %c %s %s\n", q.shape, position, flip);
    q.print();
    fmt.Printf("Rotating by %d\n", position.ori - q.enter.ori);
    q.rotate(position.ori - q.enter.ori);
    q.print();
    if flip {
      fmt.Println("Flipping");
      q.flip();
      q.print();
    }
    fmt.Printf("Translating by %d, %d\n", 3 - q.enter.x, -q.enter.y);
    q.translate(3 - q.enter.x, 0 - q.enter.y);
    q.print();

  } else { // Buggy flipswap behavior
    fmt.Println("flipswap");
    r := new_piece(source.shape, source.enter, source.exit);

    // Green: "Safety" adjustment for S and T (pieces with a hole at (3, 0))
    if r.shape == 'T' || r.shape == 'S' { r.translate(0, -1); }

    // Red: Apply normal rotation and flip computation for the source piece
    r.rotate(position.ori - r.enter.ori);
    if flip { r.flip(); }

    // TODO: Check for validity of *source* piece here.

    // Blue: Apply the source rotation and flip to the target piece, then adjust based on the source's entrance
    q.rotate(position.ori - r.enter.ori);
    if flip { q.flip(); }
    q.translate(3 - r.enter.x, 0 - r.enter.y);
  }

  q.translate(position.x, position.y);

  var name string;
  if source != nil && flip  { name = fmt.Sprintf("(%c'%c)", source.shape, p.shape); }
  if source != nil && !flip { name = fmt.Sprintf("(%c%c)", source.shape, p.shape); }
  if source == nil && flip  { name = fmt.Sprintf("%c'", p.shape); }
  if source == nil && !flip { name = fmt.Sprintf("%c", p.shape); }

  return q, name;
}

func (p *piece) place(grid [][]bool) bool {
  for _, c := range p.cells {
    if grid[c.x][c.y] {
      fmt.Printf("Attempted to place piece %c but it collided with the grid at (%d, %d)\n", p.shape, c.x, c.y);
      return false; // Collides with existing piece
    }
  }

  for _, c := range p.cells {
    grid[c.x][c.y] = true;
  }

  return true;
}

func (p *piece) unplace(grid [][]bool) {
  for _, c := range p.cells {
    grid[c.x][c.y] = false;
  }
}


