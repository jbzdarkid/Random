function toggle_click() {
  var svg = this.parentElement
  if (this.getAttribute('stroke') == 'black') {
    this.setAttribute('stroke', 'lightgray')
    this.setAttribute('opacity', 0.5)
    svg.removeChild(this)
    svg.insertBefore(this, svg.firstChild)
  } else {
    this.setAttribute('stroke', 'black')
    this.setAttribute('opacity', 1)
    svg.removeChild(this)
    svg.appendChild(this)
  }
}

function drawLine(svg, x1, y1, x2, y2) {
  var line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
  line.setAttribute('stroke', 'black')
  line.setAttribute('stroke-width', 5)
  line.setAttribute('stroke-linecap', 'round')
  line.setAttribute('x1', x1)
  line.setAttribute('y1', y1)
  line.setAttribute('x2', x2)
  line.setAttribute('y2', y2)
  svg.appendChild(line)

  line.onclick = toggle_click
  line.onclick()
  return line
}

function hideTransparent() {
  for (var line of document.getElementsByTagName('line')) {
    if (line.getAttribute('stroke') == 'lightgray') {
      line.setAttribute('opacity', 0)
    }
  }
}

window.onload = function() {
  var phonemes = document.getElementById('phonemes')
  var text = document.getElementById('text')
  for (var i=0; i<30; i++) {
    var cell = phonemes.insertCell()
    addPhoneme(cell)
    var input = document.createElement('input')
    input.style = 'width: 60px; border: none; text-align: center; font-family: Arial; font-size: 24px'
    text.insertCell().appendChild(input)
  }
}

function addPhoneme(parent) {
  var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  parent.appendChild(svg)
  svg.style = 'width: 60px; height: 100px'
  svg.setAttribute('viewbox', '0 0 60 100')
  //          (30,  5)        
  //  
  //  
  //  ( 5, 20)        (55, 20)
  //  
  //  
  //          (30, 35)
  //  
  //  ( 5, 50)(30, 50)(55, 50)
  //
  //  ( 5, 60)(30, 60)(55, 60)
  //
  //
  //  ( 5, 75)        (55, 75)
  //  
  //  
  //          (30, 90)        
  
  drawLine(svg, 30,  5,  5, 20)   // Top -> Top left
  drawLine(svg, 30,  5, 30, 35)   // Top -> Top Middle
  drawLine(svg, 30,  5, 55, 20)   // Top -> Top right
                               
  drawLine(svg,  5, 20,  5, 50)   // Top left -> Left
  drawLine(svg,  5, 20, 30, 35)   // Top left -> Middle
                               
  drawLine(svg, 30, 35, 30, 50)   // Top -> Top Middle
                               
  // drawLine(svg, 55, 20, 55, 50)   // Top right -> Right (not part of this symbol
  drawLine(svg, 55, 20, 30, 35)   // Top right -> Middle
                               
  var midline = drawLine(svg,  5, 50, 55, 50)   // Left -> Right
  midline.onclick()
  midline.onclick = null

  drawLine(svg,  5, 60,  5, 75)   // Left -> Bot Left
  drawLine(svg,  5, 75, 30, 90)   // Bot Left -> Bottom

  drawLine(svg, 30, 60,  5, 75)   // Middle -> Bot Left
  drawLine(svg, 30, 60, 30, 90)   // Middle -> Bottom
  drawLine(svg, 30, 60, 55, 75)   // Middle -> Bot Right

  // drawLine(svg, 55, 60, 55, 75)   // Right -> Bot Right (not part of this symbol)
  drawLine(svg, 55, 75, 30, 90)   // Bot Right -> Bottom

  var circ = document.createElementNS('http://www.w3.org/2000/svg', 'circle')
  svg.appendChild(circ)
  circ.setAttribute('stroke', 'black')
  circ.setAttribute('stroke-width', 5)
  circ.setAttribute('fill', 'none')
  circ.setAttribute('cx', 30)
  circ.setAttribute('cy', 90)
  circ.setAttribute('r', 5)
  circ.onclick = toggle_click
  circ.onclick()
}

