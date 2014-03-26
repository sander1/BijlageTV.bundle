NAME = 'BijlageTV'
LIVESTREAM_URL = 'http://vid1-ams.smcdn.net/bijlagetv/_definst_/smil:switch.smil/playlist.m3u8'
EPG_URL = 'http://bijlage.tv/video/epg.json'
FEATURED_ARTICLES = 'http://api.smcdn.net/api/v1/articles'

ICON = 'icon-default.jpg'
ART = 'art-default.jpg'

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	DirectoryObject.thumb = R(ICON)
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36'

####################################################################################################
@handler('/video/bijlagetv', NAME, thumb=ICON, art=ART)
def MainMenu():

	oc = ObjectContainer()

	oc.add(CreateVideoClipObject(
		url = LIVESTREAM_URL,
		title = 'Live Stream',
		resolutions = ['1080']
	))

	oc.add(DirectoryObject(key=Callback(Articles, title='Featured Articles'), title='Featured Articles'))

	return oc

####################################################################################################
@route('/video/bijlagetv/articles')
def Articles(title):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(FEATURED_ARTICLES)

	for article in json_obj:

		article = article['article']

		oc.add(CreateVideoClipObject(
			id = article['id'],
			title = article['title'],
			summary = article['summary'],
			thumb = article['poster_image'],
			originally_available_at = article['publication_date'],
			resolutions = ['576']
		))

	return oc

####################################################################################################
def CreateVideoClipObject(id=None, url=None, title=None, summary=None, thumb='', originally_available_at=None, resolutions=[], include_container=False):

	videoclip_obj = VideoClipObject(
		key = Callback(CreateVideoClipObject, id=id, url=url, title=title, summary=summary, thumb=thumb, originally_available_at=originally_available_at, resolutions=resolutions, include_container=True),
		rating_key = url if url else id,
		title = title,
		summary = summary,
		thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON),
		originally_available_at = Datetime.ParseDate(originally_available_at)
	)

	if url:
		items = [
			MediaObject(
				parts = [
					PartObject(key=HTTPLiveStreamURL(url))
				],
				video_resolution = res,
				audio_channels = 2,
				optimized_for_streaming = True
			) for res in resolutions
		]
	else:
		items = [
			MediaObject(
				parts = [
					PartObject(key=HTTPLiveStreamURL(Callback(PlayVideo, id=id, res=res)))
				],
				video_resolution = res,
				audio_channels = 2,
				optimized_for_streaming = True
			) for res in resolutions
		]

	videoclip_obj.items = items

	if include_container:
		return ObjectContainer(objects=[videoclip_obj])
	else:
		return videoclip_obj

####################################################################################################
@indirect
def PlayVideo(id, res):

	json_obj = JSON.ObjectFromURL(FEATURED_ARTICLES)

	for article in json_obj:

		article = article['article']

		if article['id'] == id:

#			if res == '1080' and 'video_url' in article:
#				video_url = '%s/playlist.m3u8' % article['link_hd']
#			else:
#				video_url = '%s/playlist.m3u8' % article['link_sd']

			video_url = '%s/playlist.m3u8' % article['link_hd']
			return IndirectResponse(VideoClipObject, key=video_url)

	raise Ex.MediaNotAvailable
