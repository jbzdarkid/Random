// ==UserScript==
// @match http://*.twitch.tv/*
// @match http://*.twitch.tv/*/v/*
// @version 1.3
// ==/UserScript==
if (window.location.pathname == "/") {
  return;
}
var host = window.location.protocol+"//"+window.location.host+"/"
var path = window.location.pathname.split('/');
var url = "";
if (path.length == 2) {
  url = host+path[1]+"/popout";
} else if (path.length == 4) {
  url = host+path[1]+"/popout?videoId="+path[2]+path[3];
  if (window.location.search !== "") {
    url += "&"+window.location.search.slice(1); // Cuts initial ?
  }
}
if (url !== "") {
  var redir = "\n<meta http-equiv=\"refresh\" content=\"0; url="+url+"\">";
  document.head.innerHTML += redir;
}