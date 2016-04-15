// ==UserScript==
// @name Full-browser Video
// @description Loads videos from Twitch and Youtube in 'full-browser', i.e. filling to the edge of the browser, but not fullscreen.
// @match http://www.twitch.tv/*
// @match https://www.twitch.tv/*
// @match http://www.youtube.com/*
// @match https://www.youtube.com/*
// @version 2.3
// ==/UserScript==

function redirect(url) {
	console.log('Full-browser video redirecting to '+url);
	window.location.replace(url);
}

var path = window.location.pathname.split('/');
var host = window.location.hostname.split('.')[1];
if (path[path.length-1] == '') { // If the url ends with a '/', like twitch.tv/
	path.pop();
}
var query = window.location.search;

if (host == 'twitch') {
	if (path.length == 2) { // Viewing a channel
		redirect('https://player.twitch.tv/?volume=1&branding=false&showInfo=false&channel='+path[1]);
	} else if (path.length == 4 && path[2] == 'v') { // Viewing a twitch vod
		redirect('https://player.twitch.tv/?volume=1&branding=false&showInfo=false&video='+path[2]+path[3]);
	}
} else if (host == 'youtube') {
	if (path[1] == 'watch') { // Watching a youtube video
		var parts = query.slice(1).split('&');
		var newParts = [];
		var videoId = null;
		for (var p=0; p<parts.length; p++) {
			if (parts[p].substring(0, 2) == 'v=') {
				videoId = parts[p].substring(2);
			} else {
				newParts.push(parts[p]);
			}
		}
		redirect('http://www.youtube.com/embed/'+videoId+'?'+newParts.join('&'));
	}
}
