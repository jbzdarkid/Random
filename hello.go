package main

import "fmt"

func main() {
  // fmt.Println("hello" + " world");
  // var a = 10;
  // a += 20;
  // 
  // b := 10;
  // fmt.Println(a + b);
  // 
  // i := 0
  // for ; i < 3; i++ {
    // fmt.Println(i);
  // }
  // 
  // arr := [10]int {1, 2, 3, 4};
  // fmt.Println(arr);
  // 
  // dynarr := make([]int64, 10);
  // dynarr[8] = 8;
  // dynarr = append(dynarr, 11);
  // fmt.Println(dynarr);
  // 
  // i = ident(i);
  // 
  // var m = map[string]int{};
  // m["N2"] = 3
  // m["N3"] = 10
  // fmt.Println(m);

  var e1_pieces = make([]piece, 8)
  e1_pieces[0] = new_piece('S', loc{3.5, 1},  loc{0.5, 0});
  e1_pieces[1] = new_piece('O', loc{3, -0.5}, loc{2, 1.5});
  e1_pieces[2] = new_piece('L', loc{3.5, 1},  loc{0.5, 0});
  e1_pieces[3] = new_piece('O', loc{2, -1}, loc{3, 2});
  e1_pieces[4] = new_piece('S', loc{4, 1},  loc{0, 0});
  e1_pieces[5] = new_piece('L', loc{3, 2},  loc{1, -1});
  e1_pieces[6] = new_piece('L', loc{3, 2},  loc{0, 0});
  e1_pieces[7] = new_piece('L', loc{4, 1},  loc{1, 1});

  for _, p := range e1_pieces {
    p.print()
  }

  solve_bridge(e1_pieces[0:2], loc{-0.5,0}, loc{-8,-1}); // 8 units forward, 1 unit left.
}

func solve_bridge(pieces []piece, start loc, end loc) {
  // Large to have scratch space.
  grid := make([][]bool, 100);
  for x := range(grid) { grid[x] = make([]bool, 100); }
  grid[50][50] = true; // Always the start point (so 0,0 == 50,50)
  grid[49.5 + end.x][50 + end.y] = true;

  solve_bridge_recursive(grid, pieces, loc{start.x+50, start.y+50});
}

func solve_bridge_recursive(grid [][]bool, pieces []piece, current loc) {
  any := false
  for i, p := range pieces {
    if p.shape == rune(0) { continue; }
    any = true

    for option := 0; option < 8; option++ {
      rotation := option % 4;
      flip := (option % 8) / 4;
      q = p.transform(rotation, current, flip, nil);
      placed, new_current := q.place(grid, current);
      if placed {
        pieces[i].shape = rune(0) // Placeholder to indicate that we have placed this shape
        solve_bridge_recursive(grid, pieces, new_current);
        pieces[i].shape = p.shape
        q.unplace(grid, current)
      }
    }
  }

  if !any {
    fmt.Println("Recursion endpoint");
  }
}


type loc struct { x float64; y float64 }

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

  return p;
}

func (p piece) contains (l loc) {
  for _, c := p.cells {
    if c == loc { return true; }
  }
  return false;
}

func (p piece) print() {
  output := "+----+\n";
  for x := 0.0; x < 4; x++ {
    output += "|";
    for y := 0.0; y < 4; y++ {
      for _, c := p.cells
      switch {
        case !p.cells.contains(loc{x, y})         output += " ";
        case p.enter == loc{x-0.5, y}:            output += "v";
        case p.enter == loc{x+0.5, y}:            output += "^";
        case p.enter == loc{x, y-0.5}:            output += ">";
        case p.enter == loc{x, y+0.5}:            output += "<";
        case p.exit == loc{x-0.5, y}:             output += "^";
        case p.exit == loc{x+0.5, y}:             output += "v";
        case p.exit == loc{x, y-0.5}:             output += "<";
        case p.exit == loc{x, y+0.5}:             output += ">";
        default:                                  output += "#";
      }
    }
    output += "|\n";
  }
  output += "+----+\n";
  fmt.Print(output)
}

/**
 * Rotate, translate, flip, or flipswap a piece (before placing it)
 * rotation: Integer, number of 90 degree clockwise rotations.
 * translation: Loc, reference point for the start of the 
 *   Note: Translations can result in a piece shifted by 0.5 from the grid
 * flip: Boolean, if the piece is flipped (or the source piece is flipped, if nonnil
 * source: &Piece, the flipswap source piece. See this video for an explanation.
 *   https://youtu.be/OLKT43q9EYY
 *   Optional value indicated by nil, in which case no flipswap is applied.
**/
func (p piece) transform(rotation int, translation loc, flip bool, source *piece) piece {
  q := new_piece(p.shape, p.start, p.end); // Copy and we'll just modify the copy

  if source == nil { // Normal, non-flipswap behavior.
    for j := 0; j < rotation; j++ {
      q.start = loc{4 - q.start.y, q.start.x};
      q.end   = loc{4 - q.end.y,   q.end.x};
      for i, loc := range q.locs {
        q.locs[i] = loc{4 - loc.y, loc.x};
      }
    }

    if flip {
      q.start = loc{3 - q.start.x, q.start.y};
      q.end   = loc{3 - q.end.x,   q.end.y};
      for i, loc := range q.locs {
        q.locs[i] = loc{3 - loc.x, loc.y};
      }
    }

  } else { // Buggy flipswap behavior

    // TODO

  }

  // Translation is always last, since it's relative to the grid overall
  dx := translation.x - q.start.x
  dy := translation.y - q.start.y
  for i, loc := range q.locs {
    q.locs[i] = loc{loc.x - dx, loc.y - dy};
  }

  return q
}

func (p piece) place(grid [][]bool, target loc) (bool, loc) {
  dx := target.x - p.start.x;
  dy := target.y - p.start.y;
  if dx != int(dx) || dy != int(dy) { return false, target; } // Not oriented properly

  for _, c := range p.cells {
    if grid[dx + c.x][dy + c.y] { return false, target; } // Collides with existing piece
  }

  for _, c := range p.cells {
    grid[dx + c.x][dy + c.y] = true;
  }

  return true, loc{dx + p.end.x, dy + p.end.y};
}

func (p piece) unplace(grind [][]bool, target loc) {
  dx := target.x - p.start.x
  dy := target.y - p.start.y
  for _, c := range p.cells {
    grid[dx + c.x][dy + c.y] = false;
  }
}


