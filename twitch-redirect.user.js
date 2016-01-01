// ==UserScript==
// @match http://*.twitch.tv/*
// @version 1.6
// ==/UserScript==

var url = "";
var path = window.location.pathname.split('/');

if (path.length == 2 && path[1] !== "") { // twitch.tv/channel but not twitch.tv/ or player.twitch.tv/
	url = "&html5&channel="+path[1];
} else if (path.length == 4) {
	if (path[2] == "profile") { // twitch.tv/channel/profile/highlights
  	console.log("Path: "+path);
  	// For videos in past broadcasts/highlights, the page isn't reloaded when you click them, so I change the url.
		setTimeout(function(){
			var body = document.body.innerHTML;
			document.body.innerHTML = body.replace(/http:\/\/www\.twitch\.tv\/([\w\d]*)\/v\/(\d*)/g, "http://player.twitch.tv/?branding=false&showInfo=false&video=v$2");
		}, 5000); // 5 second delay while page loads
	} else { // twitch.tv/channel/v/numbers
		url = "&video="+path[2]+path[3];
	}
}
if (url !== "") {
	url = "http://player.twitch.tv/?branding=false&showInfo=false" + url
	if (window.location.search !== "") { // Query string
		url += "&"+window.location.search.slice(1); // Cuts initial ?
	}
	var redir = "\n<meta http-equiv=\"refresh\" content=\"0; url="+url+"\">";
	document.head.innerHTML += redir;
}
