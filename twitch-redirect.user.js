// ==UserScript==
// @match http://*.twitch.tv/*
// @version 1.5
// ==/UserScript==

var url = "";
var path = window.location.pathname.split('/');
var host = window.location.protocol+"//"+window.location.host+"/"
if (path.length == 2 && window.location.pathname != "/") {
  url = host+path[1]+"/popout";
} else if (path.length == 4 && path[2] != "profile") {
  url = host+path[1]+"/popout?videoId="+path[2]+path[3];
  if (window.location.search !== "") {
    url += "&"+window.location.search.slice(1); // Cuts initial ?
  }
}
if (url !== "") {
  var redir = "\n<meta http-equiv=\"refresh\" content=\"0; url="+url+"\">";
  document.head.innerHTML += redir;
}

// var body = document.body.innerHTML;
// var find1 = /href="http:\/\/www\.twitch\.tv\/([a-zA-Z0-9]*)\/v\/([0-9]*)\?/;
// var replace1 = /href="http:\/\/www.twitch.tv\/$1\/popout?videoId=$2&/;
// var find2 = /href="http:\/\/www\.twitch\.tv\/([a-zA-Z0-9]*)\/v\/([0-9]*)/;
// var replace2 = /href="http:\/\/www.twitch.tv\/$1\/popout?videoId=$2/;
// var find3 = /twitch\.tv\/([a-zA-Z0-9]*)/;
// var replace3 = /twitch.tv\/$1\/popout/;
// console.log(body.search(/twitch\.tv\/([a-zA-Z0-9]*)/));
// body.replace(find1, 'asdf1');
// body.replace(find2, replace2);
// body.replace(find3, replace3);
// document.body.innerHTML = body;