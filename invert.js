var invert = document.getElementById('invert');
if (invert != null) {
  invert.parentElement.removeChild(invert);
} else {
  invert = document.createElement('style');
  document.head.appendChild(invert);
  invert.type = 'text/css';
  invert.id = 'invert';
  invert.innerHTML = 'html {-webkit-filter: invert(100%) }';
  /*invert.innerHTML = `
  html {
    color: #bfbfbf;
    background-image: none !important;
    background: #1f1f1f !important;
  }
  body, body > .container {
    background-color: #1f1f1f;
    background-image: none !important;
  }
  input, select, textarea, button {
    color: #bfbfbf;
    background-color: #1f1f1f;
  }
  text { fill: #bfbfbf; }
  font { color: #bfbfbf; }
  a { color: #8c8cfa; }

  .pdfViewer, embed[type="application/pdf"] {
    filter:invert(90%);
  }

  <!-- webkit-scrollbar is not supported by firefox -->
  *::-webkit-scrollbar-track-piece {    background-color:rgba(255, 255, 255, 0.2) !important;  }  *::-webkit-scrollbar-track {    background-color:rgba(255, 255, 255, 0.3) !important;  }  *::-webkit-scrollbar-thumb {    background-color:rgba(255, 255, 255, 0.5) !important;  }`*/
}