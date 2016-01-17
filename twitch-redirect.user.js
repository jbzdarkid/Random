// ==UserScript==
// @match http://*.twitch.tv/*
// @version 1.6
// ==/UserScript==

var player_base = "http://player.twitch.tv/?branding=false&showInfo=false";
var url = "";
var path = window.location.pathname.split('/');
if (path[path.length-1]) == "") { // If the url ends with a '/', like twitch.tv/
	path.pop();
}

if (path.length == 2) {
	// Detecting if stream is live requires https, and I don't have a safe way to do that.
	url = player_base+"&channel="+path[1];
} else if (path.length == 4) {
	if (path[2] == "profile") { // twitch.tv/channel/profile/highlights
	/* This block isn't working well; it makes loads longer and occasionally fail.
  	console.log("Path: "+path);
  	// For videos in past broadcasts/highlights, the page isn't reloaded when you click them, so I change the url.
		setTimeout(function(){
			var body = document.body.innerHTML;
			document.body.innerHTML = body.replace(/http:\/\/www\.twitch\.tv\/([\w\d]*)\/v\/(\d*)/g, "http://player.twitch.tv/?branding=false&showInfo=false&video=v$2");
		}, 5000); // 5 second delay while page loads
	*/
	} else { // twitch.tv/channel/v/numbers
		url = player_base+"&video="+path[2]+path[3];
	}
}
if (url !== "") {
	if (window.location.search !== "") { // Query string
		url += "&"+window.location.search.slice(1); // Cuts initial ?
	}
	var redir = "\n<meta http-equiv=\"refresh\" content=\"0; url="+url+"\">";
	document.head.innerHTML += redir;
}
