videos = []
for (var video of document.getElementsByTagName('ytd-grid-video-renderer')) {
  var link = video.querySelector('#thumbnail').getAttribute('href')
  var title = video.querySelector('#video-title').innerText
  var views = video.querySelector('#metadata-line').children[0].innerText

  var viewcount = 0
  if (video_views.endsWith('B views')) {
    viewcount = parseFloat(views.substr(0, views.length-7)) * 1000000000
  } else if (video_views.endsWith('M views')) {
    viewcount = parseFloat(views.substr(0, views.length-7)) * 1000000
  } else if (video_views.endsWith('K views')) {
    viewcount = parseFloat(views.substr(0, views.length-7)) * 1000
  } else {
    viewcount = parseFloat(views.substr(0, views.length-6))
  }
  videos.push([viewcount, title, link])
}
videos.sort((a, b) => a[0] - b[0])
for (video of videos) {
  console.log(video[1], 'https://youtube.com' + video[2])
}

// https://www.youtube.com/channel/UCqECaJ8Gagnn7YCbPEzWH6g