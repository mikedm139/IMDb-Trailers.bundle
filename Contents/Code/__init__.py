
PLUGIN_PREFIX = "/video/IMDBTrailers"

TRAILERS     = "http://www.imdb.com/features/video/trailers"
CONTENT_URL  = "http://www.imdb.com/video/trailers/data/_ajax/adapter/shoveler?list=%s&caller_name=ava_video_trailers" #"http://www.imdb.com/video/trailers/data/_json?list=%s"
DETAILS_PAGE = "http://www.imdb.com/video/imdb/%s/html5"

SORT_POPULAR = "popular"
SORT_RECENT  = "recent"

SORT_PREFS_KEY = "sortOrder"

CACHE_TIME = 3600


####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "IMDb HD Trailers", "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = L('IMDb HD Trailers')
  MediaContainer.art = R('art-default.jpg')
  DirectoryItem.thumb = R('icon-default.png')
  HTTP.CacheTime = CACHE_TIME

####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup='List')
    dir.Append(Function(DirectoryItem(HDVideos, title="Recent HD Trailers"), sort="recent"))
    dir.Append(Function(DirectoryItem(HDVideos, title="Popular HD Trailers"), sort="top_hd"))
    dir.Append(Function(DirectoryItem(HDVideos, title="Popular Movies"), sort="popular"))
    return dir

####################################################################################################
def HDVideos(sender, sort):
  dir = MediaContainer(viewGroup='Details')
  contentUrl = CONTENT_URL % sort
  content = JSON.ObjectFromURL(contentUrl)
  for video in content['model']['items']:
    videoId = video['video']['videoId']
    thumb = video['video']['slateUrl']
    title = video['display']['text'] + ' - ' + video['video']['title']
    duration = 1000*int(video['video']['duration']['seconds'])
    summary = video['overview']['plot']
    dir.Append(Function(VideoItem(PlayVideo, title=title, summary=summary, thumb=thumb, duration=duration), ext='mp4', videoId = videoId))
  return dir


####################################################################################################
# TODO: expand content by parsing TRAILERS, although the above seems to be their way ahead
def Videos(sender):
    dir = MediaContainer(viewGroup='Details')
    return dir
    
####################################################################################################
def PlayVideo(sender, videoId):
    detailsUrl = DETAILS_PAGE % (videoId)
    details = HTTP.Request(detailsUrl).content
    index = details.find('mp4_h264')
    start = details.find('http', index)
    end = details.find("'", start)
    videoUrl = details[start:end]
    return Redirect(videoUrl)