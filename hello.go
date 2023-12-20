package main

import "fmt"
import "os"

// Maybe just list<solution> and include loc in the soln object?
var solutions = make(map[string]loc);

func main() {
  var e1_pieces = make([]*piece, 8);
  e1_pieces[0] = new_piece('S', loc{3.5, 1},  loc{0.5, 0});
  e1_pieces[1] = new_piece('O', loc{3, -0.5}, loc{2, 1.5});
  e1_pieces[2] = new_piece('L', loc{3.5, 1},  loc{0.5, 0});
  e1_pieces[3] = new_piece('O', loc{2, -1}, loc{3, 2});
  e1_pieces[4] = new_piece('S', loc{4, 1},  loc{0, 0});
  e1_pieces[5] = new_piece('L', loc{3, 2},  loc{1, -1});
  e1_pieces[6] = new_piece('L', loc{3, 2},  loc{0, 0});
  e1_pieces[7] = new_piece('L', loc{4, 1},  loc{1, 1});

  solve_bridge(e1_pieces[0:3], loc{-0.5,0}, loc{-8.5,-1}); // 8 units forward, 1 unit left.
}

func solve_bridge(pieces []*piece, enter loc, exit loc) {
  // Large to have scratch space.
  grid := make([][]bool, 100);
  for x := range(grid) { grid[x] = make([]bool, 100); }
  grid[50][50] = true; // Always the enter point (so 0,0 == 50,50)
  grid[int(50 + exit.x)][int(50 + exit.y)] = true;

  fmt.Println("Building a bridge with these pieces:");
  for _, p := range pieces {
    p.print();
  }

  solve_bridge_recursive(
    grid,
    pieces,
    loc{enter.x+50, enter.y+50}, // position
    loc{exit.x+50, exit.y+50}, // target
    soln{}, // solution buffer
  );
}

func solve_bridge_recursive(grid [][]bool, pieces []*piece, position loc, target loc, s soln) {
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

    for option := 0; option < 6; option++ {
      flip := (option % 2) == 0;
      flipswap := (option % 6) / 2;
      var source *piece
      if flipswap == 0 { source = nil; }
      if flipswap == 1 { source = prev_piece; }
      if flipswap == 2 { source = next_piece; }
      q, name := p.transform(flip, source);

      placed := q.place(grid, position);
      if placed {
        s.push(name);

        pieces[i].shape = rune(0) // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, q.exit, target, s);
        pieces[i].shape = q.shape;

        s.pop();
        q.unplace(grid, position);
      }
    }
  }

  solutions[s.tostring()] = position
  os.Exit(0);
}

// inexplicably there are no dynamic lists. Okay, go.
type soln struct {
  data  [100]string;
  count int;
  cost  int;
}

func (s soln) push (val string) {
  s.data[s.count] = val;
  s.count++;
}

func (s soln) pop () string {
  if s.count == 0 { return ""; }
  s.count--;
  return s.data[s.count];
}

func (s soln) tostring () string {
  acc := "";
  for i := 0; i < s.count; i++ {
    if len(acc) != 0 { acc += ", "; }
    acc += s.data[i];
  }
  return acc;
}

type loc struct { x float64; y float64 }

type piece struct {
  shape rune;
  enter loc;
  exit  loc;
  cells [4]loc;
  ori   int; // 0: North, 1: West, 2: South, 3: East
};

func new_piece(shape rune, enter loc, exit loc) *piece {
  p := new(piece);
  p.shape = shape;
  p.enter = enter;
  p.exit  = exit;

  switch p.shape {
  case 'I':
    p.cells = [4]loc{loc{0, 0}, loc{1, 0}, loc{2, 0}, loc{3, 0}};
  case 'L':
    p.cells = [4]loc{loc{1, 0}, loc{2, 0}, loc{3, 0}, loc{3, 1}};
  case 'S':
    p.cells = [4]loc{loc{1, 0}, loc{2, 0}, loc{2, 1}, loc{3, 1}};
  case 'O':
    p.cells = [4]loc{loc{2, 0}, loc{2, 1}, loc{3, 0}, loc{3, 1}};
  case 'T':
    p.cells = [4]loc{loc{2, 0}, loc{2, 1}, loc{2, 2}, loc{3, 1}};
  }

  for _, cell := range p.cells {
    if cell.x == p.enter.x - 0.5 && cell.y == p.enter.y {
      p.ori = 0; // North
      break;
    } else if cell.x == p.enter.x + 0.5 && cell.y == p.enter.y {
      p.ori = 2; // South
      break;
    } else if cell.x == p.enter.x && cell.y == p.enter.y - 0.5 {
      p.ori = 3; // East
      break;
    } else if cell.x == p.enter.x && cell.y == p.enter.y + 0.5 {
      p.ori = 1; // West
      break;
    }
  }

  return p;
}

func (p piece) contains (l loc) bool {
  for _, c := range p.cells {
    if c == l { return true; }
  }
  return false;
}

func (p piece) print() {
  output := "+----+\n";
  for x := 0.0; x < 4; x++ {
    output += "|";
    for y := 0.0; y < 4; y++ {
      switch {
        case !p.contains(loc{x, y}):   output += " ";
        case p.enter == loc{x-0.5, y}: output += "v";
        case p.enter == loc{x+0.5, y}: output += "^";
        case p.enter == loc{x, y-0.5}: output += ">";
        case p.enter == loc{x, y+0.5}: output += "<";
        case p.exit  == loc{x-0.5, y}: output += "^";
        case p.exit  == loc{x+0.5, y}: output += "v";
        case p.exit  == loc{x, y-0.5}: output += "<";
        case p.exit  == loc{x, y+0.5}: output += ">";
        default:                       output += "#";
      }
    }
    output += "|\n";
  }
  output += "+----+\n";
  fmt.Print(output);
}

// rotation: Integer, number of 90 degree clockwise rotations.
func (p *piece) rotate(rotation int) {
  for i := 0; i < rotation; i++ {
    p.enter = loc{4 - p.enter.y, p.enter.x};
    p.exit  = loc{4 - p.exit.y,  p.exit.x};
    for i, cell := range p.cells {
      p.cells[i] = loc{4 - cell.y, cell.x};
    }
  }
}

func (p *piece) flip() {
  p.enter = loc{3 - p.enter.x, p.enter.y};
  p.exit  = loc{3 - p.exit.x,  p.exit.y};
  for i, cell := range p.cells {
    p.cells[i] = loc{3 - cell.x, cell.y};
  }
}

func (p *piece) translate(trans loc) {
  p.enter = loc{p.enter.x + trans.x, p.enter.y + trans.y};
  p.exit  = loc{p.exit.x + trans.x,  p.exit.y + trans.y};
  for i, cell := range p.cells {
    p.cells[i] = loc{cell.x + trans.x, cell.y + trans.y};
  }
}

/**
 * Rotate, translate, flip, or flipswap a piece (before placing it)
 * flip: Boolean, if the piece is flipped (or the source piece is flipped, if nonnil
 * source: &Piece, the flipswap source piece. See this video for an explanation.
 *   https://youtu.be/OLKT43q9EYY
 *   Optional value indicated by nil, in which case no flipswap is applied.
**/
func (p piece) transform(flip bool, source *piece) (*piece, string) {
  q := new_piece(p.shape, p.enter, p.exit); // Copy and we'll just modify the copy

  if source == nil { // Normal, non-flipswap behavior.
    q.rotate(q.ori);
    if flip { q.flip(); }

  } else { // Buggy flipswap behavior
    r := new_piece(source.shape, source.enter, source.exit);
    r.print()

    // Green: "Safety" adjustment for S and T (pieces with a hole at (3, 0))
    if r.shape == 'T' || r.shape == 'S' { r.translate(loc{0, -1}); }
    r.print()

    // Red: Apply normal rotation and flip computation for the source piece
    r.rotate(r.ori);
    r.print()
    if flip { r.flip(); }
    r.print()

    // Blue: Apply the source rotation and flip to the target piece, then adjust based on the source's entrance
    q.rotate(r.ori);
    q.print()
    if flip { q.flip(); }
    q.print()
    q.translate(loc{-r.enter.x, -r.enter.y});
    q.print()
  }

  var name string;
  if source != nil && flip  { name = fmt.Sprintf("(%c'%c)", source.shape, p.shape); }
  if source != nil && !flip { name = fmt.Sprintf("(%c%c)", source.shape, p.shape); }
  if source == nil && flip  { name = fmt.Sprintf("%c'", p.shape); }
  if source == nil && !flip { name = fmt.Sprintf("%c", p.shape); }

  return q, name;
}

func (p piece) place(grid [][]bool, pos loc) bool {
  for _, c := range p.cells {
    if grid[int(c.x + pos.x)][int(c.y + pos.y)] { return false; } // Collides with existing piece
  }

  for _, c := range p.cells {
    grid[int(c.x + pos.x)][int(c.y + pos.y)] = true;
  }

  return true;
}

func (p piece) unplace(grid [][]bool, pos loc) {
  for _, c := range p.cells {
    grid[int(c.x + pos.x)][int(c.y + pos.y)] = false;
  }
}


