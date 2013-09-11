import re
 
PLUGIN_PREFIX = "/video/IMDBTrailers"

TRAILERS     = "http://www.imdb.com/features/video/trailers"
CONTENT_URL  = "http://www.imdb.com/video/trailers/data/_ajax/adapter/shoveler?list=%s&caller_name=ava_video_trailers"
DETAILS_PAGE = "http://www.imdb.com/video/imdb/%s/html5"

HEADERS = {"referer":"http://www.imdb.com/trailers"}

MediaObject.container = 'mp4'
MediaObject.audio_codec = 'aac'
MediaObject.video_codec = 'h264'
MediaObject.optimized_for_streaming = True
MediaObject.audio_channels = 2

####################################################################################################
def Start():
  ObjectContainer.title1 = L('IMDb HD Trailers')
  ObjectContainer.art = R('art-default.jpg')
  DirectoryObject.thumb = R('icon-default.png')
  
####################################################################################################
@handler(PLUGIN_PREFIX, "IMDb HD Trailers", "icon-default.png", "art-default.jpg", allow_sync=True)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="recent", title="Recent HD Trailers"), title="Recent HD Trailers"))
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="top_hd", title="Popular HD Trailers"), title="Popular HD Trailers"))
  oc.add(DirectoryObject(key=Callback(HDVideos, sort="popular", title="Popular Movies"), title="Popular Movies"))
  return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/hdvideos', allow_sync=True)
def HDVideos(sort, title):
  oc = ObjectContainer(title2=title)
  cookies = HTTP.CookiesForURL(TRAILERS)
  oc.http_cookies = cookies
  contentUrl = CONTENT_URL % sort
  content = JSON.ObjectFromURL(contentUrl, headers=HEADERS)
  for video in content['model']['items']:
    videoId = video['video']['videoId']
    thumb = video['display']['poster']['url']
    try:
      thumb = thumb.replace('_SY209_CR0,0,141,209_', '_SY836_CR0,0,564,836_')
      thumb = thumb.replace('_SX141_CR0,0,141,209_', '_SX564_CR0,0,564,836_')
    except:
      thumb = video['video']['slateUrl']
    title = unescape(video['display']['text'] + ' - ' + video['video']['title'])
    duration = 1000*int(video['video']['duration']['seconds'])
    try:summary = unescape(video['overview']['plot'])
    except:
      Log('Error unescaping summary for "%s"' % title)
      summary = video['overview']['plot']
    directors = video['overview']['directors']
    genres = video['overview']['genres']
    oc.add(CreateTrailerObject(title, summary, thumb, duration, directors, genres, videoId))
  return oc

####################################################################################################
@route(PLUGIN_PREFIX+'/trailer', directors = list, duration = int, genres = list)
def CreateTrailerObject(title, summary, thumb, duration, directors, genres, videoId, include_container=False):  
  trailer = MovieObject(
    key = Callback(CreateTrailerObject, title=title, summary=summary, thumb=thumb, duration=duration, directors=directors, genres=genres, videoId=videoId, include_container=True),
    rating_key = DETAILS_PAGE % videoId,
    title = title,
    summary = summary,
    thumb = thumb,
    duration = duration,
    directors = directors,
    genres = genres,
    items = [
      MediaObject(
	parts = [PartObject(key=Callback(PlayVideo, videoId=videoId, res='720'))],
	video_resolution = '720'
	),
      MediaObject(
	parts = [PartObject(key=Callback(PlayVideo, videoId=videoId, res='480'))],
	video_resolution = '480'
      )	
    ]
  )
  
  if include_container:
    return ObjectContainer(objects=[trailer])
  else:
    return trailer

####################################################################################################
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

####################################################################################################
def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print "erreur de valeur"
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
         except KeyError:
            print "keyerror"
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)