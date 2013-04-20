
PLUGIN_PREFIX = "/video/IMDBTrailers"

TRAILERS     = "http://www.imdb.com/features/video/trailers"
CONTENT_URL  = "http://www.imdb.com/video/trailers/data/_ajax/adapter/shoveler?list=%s&caller_name=ava_video_trailers"
DETAILS_PAGE = "http://www.imdb.com/video/imdb/%s/html5"

####################################################################################################
def Start():
  ObjectContainer.title1 = L('IMDb HD Trailers')
  ObjectContainer.art = R('art-default.jpg')
  DirectoryObject.thumb = R('icon-default.png')
  
####################################################################################################
@handler(PLUGIN_PREFIX, "IMDb HD Trailers", "icon-default.png", "art-default.jpg")
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="recent", title="Recent HD Trailers"), title="Recent HD Trailers"))
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="top_hd", title="Popular HD Trailers"), title="Popular HD Trailers"))
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="popular", title="Popular Movies"), title="Popular Movies"))
  return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/hdvideos')
def HDVideos(sort, title):
  oc = ObjectContainer(title2=title)
  contentUrl = CONTENT_URL % sort
  content = JSON.ObjectFromURL(contentUrl)
  for video in content['model']['items']:
    videoId = video['video']['videoId']
    thumb = video['display']['poster']['url']
    try:
      thumb = thumb.replace('_SY209_CR0,0,141,209_', '_SY836_CR0,0,564,836_')
      thumb = thumb.replace('_SX141_CR0,0,141,209_', '_SX564_CR0,0,564,836_')
    except:
      thumb = video['video']['slateUrl']
    title = video['display']['text'] + ' - ' + video['video']['title']
    duration = 1000*int(video['video']['duration']['seconds'])
    summary = video['overview']['plot'].replace('&#x22;','"').replace("&#x27;", "'")
    directors = video['overview']['directors']
    genres = video['overview']['genres']
    oc.add(CreateTrailerObject(title, summary, thumb, duration, directors, videoId))
  return oc

####################################################################################################
@route(PLUGIN_PREFIX+'/trailer')
def CreateTrailerObject(title, summary, thumb, duration, directors, videoId, include_container=False):
  return MovieObject(
    key = Callback(CreateTrailerObject, title=title, summary=summary, thumb=thumb, duration=duration, directors=directors, videoId=videoId, include_container=True),
    rating_key = DETAILS_PAGE % videoId,
    title = title,
    summary = summary,
    thumb = thumb,
    duration = duration,
    directors = directors,
    items = [
      MediaObject(
	parts = [PartObject(key=Callback(PlayVideo, videoId=videoId, res='720'))],
	container = Container.MP4,
	audio_codec = AudioCodec.AAC,
	video_codec = VideoCodec.H264,
	video_resolution = '720',
	audio_channels = 2,
	optimized_for_streaming = True
      ),
      MediaObject(
	parts = [PartObject(key=Callback(PlayVideo, videoId=videoId, res='480'))],
	container = Container.MP4,
	audio_codec = AudioCodec.AAC,
	video_codec = VideoCodec.H264,
	video_resolution = '480',
	audio_channels = 2,
	optimized_for_streaming = True
      )
    ]
  )
  
def PlayVideo(videoId, res='720'):
  if res == '720':
    detailsUrl = DETAILS_PAGE % (videoId) + "?format=720p"
  else:
    detailsUrl = DETAILS_PAGE % (videoId)
  details = HTTP.Request(detailsUrl).content
  index = details.find('mp4_h264')
  start = details.find('http', index)
  end = details.find("'", start)
  videoUrl = details[start:end]
  return Redirect(videoUrl)