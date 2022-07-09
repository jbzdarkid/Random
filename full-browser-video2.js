var hostParts = window.location.hostname.split('.');
var host = hostParts[hostParts.length - 2];

function openYoutube(video, list) {
  var location = 'https://www.youtube.com/embed/' + video;
  if (list) location += '?list=' + list;
  window.location = location;
}

function openTwitch(channel, video) {
  var location = 'https://player.twitch.tv/?parent=twitch.tv&player=popout&autoplay=false&branding=false&showInfo=false';
  if (video)   location += '&video=' + pathParts[2];
  if (channel) location += '&channel=' + pathParts[1];
  window.location = location;
}

if (host == 'youtube') {
  var videoUrl = document.getElementById('movie_player').getVideoUrl();
  var video = videoUrl.match(/v=([^?&]+)/)[1];
  var list = (videoUrl.match(/list=([^?&]+)/) || [])[1];
  openYoutube(video, list);
} else if (host == 'twitch') {
  var pathParts = window.location.pathname.split('/');
  if (pathParts[1] == 'videos') openTwitch(null, pathParts[2]);
  else                          openTwitch(pathParts[1], null);
} else /* embedded video, not working */ {
  var youtubeEmbed = document.getElementsByClassName('youtube')[0];
  if (youtubeEmbed) {
    var video = youtubeEmbed.src.match(/\/embed\/([^?&]+)/)[1];
    var list = (youtubeEmbed.src.match(/[?&]list=([^&?]+)/) || [])[1];
    openYoutube(video, list);
  }
  var twitchEmbed = document.getElementsByClassName('twitch')[0];
  if (twitchEmbed) {
    var video = (twitchEmbed.src.match(/[?&]video=v(\d+)/) || [])[1];
    var channel = (twitchEmbed.src.match(/[?&]channel=([^?&]+)/) || [])[1];
    openTwitch(video, channel);
  }
}