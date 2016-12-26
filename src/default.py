__version__ = "1.94"

import urllib, urllib2
import xbmcplugin, xbmcgui, xbmc, xbmcaddon
import re, sys, cgi, os
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from BeautifulSoup import BeautifulSoup
import unicodedata
import xml.etree.ElementTree as ET
import time
import update
#import downloader
#from pprint import pprint

try:
    import json
except ImportError:
    import simplejson as json

programPath  = xbmcaddon.Addon().getAddonInfo('path')


try:
   import StorageServer
except:
   try:
      import storageserverdummy as StorageServer
   except ImportError:
      update.downloadPythonFile(programPath, 'storageserverdummy.py')
      import storageserverdummy as StorageServer

#import StorageServer

#version 1.1

BASE_URL       = "http://www.tubetamil.com/"
MOVIE_URL      = "http://tamilbase.com/category/s3-movies/c159-latest-movei/"
MOVIE_RAJ_URL  = "http://www.rajtamil.com/category/movies/"
vijayVODUrl    = "http://tamilkodi.com/tkodi/vijaytvvod.php"
EINTHUSAN      = "http://www.einthusan.com/"
raj_vijay_serial = "http://www.rajtamil.com/category/vijay-tv-serial/"
raj_vijay_shows = "http://www.rajtamil.com/category/vijay-tv-shows/"
MOVIE_GUN_MOVI = "http://tamilgun.com/categories/movies/"
TAMIL_GUN_HD = "http://tamilgun.com/categories/hd-movies/"
LIVE_TV1       = "http://www.tamilkodi.com/tkodi/check.php"
LIVE_RADIO     = "http://www.tamilkodi.com/tkodi/check.php?radio"
__SPORTS__     = "http://www.tamilkodi.com/tkodi/check.php?sport"
__AKASH__      = "http://tamilkodi.com/tkodi/check.php?akash"
fanartimg      = 'https://lh3.googleusercontent.com/-DXYu2Mm04hE/VTBYG9U1x2I/AAAAAAAACPM/VZ6bE_XKyCk/s1600-Ic42/fanart.jpg'

net            = Net()
addonId        = 'plugin.video.tamilkodi'
addon_settings = xbmcaddon.Addon(id = addonId);
addon          = Addon( addonId, sys.argv )
addonPath      = xbmc.translatePath( addon.get_path() )
resPath        = os.path.join( addonPath, 'resources' )
iconPath       = os.path.join( resPath, 'images' )
addon_handle   = int(sys.argv[1])
base_url       = sys.argv[0]
xbmcplugin.setPluginFanart(int(sys.argv[1]), fanartimg, color2='0xFFFF3300')

programPath    = xbmcaddon.Addon().getAddonInfo('path')

cache = StorageServer.StorageServer( addonId )
cache.dbg = True

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def getImgPath( icon ):
    icon = icon + '.png'
    imgPath = os.path.join( iconPath, icon )
   # print imgPath
    if os.path.exists( imgPath ):
        return imgPath
    else:
        return ''

def pathJoin(img):
    imgpath = os.path.join( addonPath, "images" )
    return os.path.join( imgpath, img )

def getVersion():
    print 'get version, ',__version__
    return float(__version__)

def settings(action = None ):
    if(action == 'thumb'):
        xbmc_texture_path = os.path.join(xbmc.translatePath('special://home'), 'userdata/Database/Textures13.db')
        try:
            os.remove(xbmc_texture_path)
            addon.show_ok_dialog( [ 'Please Restart XBMC/KODI' ], title='Thumbnail Cache Removed' )
            print 'im done'
        except:
            pass

        print 'thumb'


    li = xbmcgui.ListItem('Remove Thumbnail Cache' , thumbnailImage=getImgPath('RemoveThumbCache'))
    urlQuery = build_url({ 'mode' : 'settings', 'url' : 'thumb', 'title' : 'Remove Thumbnail Cache' , 'iconImg' : getImgPath('RemoveThumbCache')})
    xbmcplugin.addDirectoryItem(handle = addon_handle, url = urlQuery, listitem = li, isFolder = True)
    xbmcplugin.endOfDirectory(addon_handle)
    thumbnailView()

def addItem(name, img, url):
    li = xbmcgui.ListItem(name, thumbnailImage=img)
    if len(url)==2:
        #print 'regexed', len(url)
        channelLink, channelRegex = url
        url = build_url({'mode' : 'playvideo', 'url' :  channelLink, 'regex' : channelRegex, 'name' : name, 'iconImg' : img})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    else:
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


def open_url( url, referer = None, user_agent = None):
    if not referer:
        referer = url
    if not user_agent:
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1'
    try:
        req = urllib2.Request( url )
        req.add_header('User-Agent', user_agent)
        req.add_header('Referer', referer)
        response = urllib2.urlopen(req)
        html = response.read()
        return html
    except urllib2.HTTPError, e:
        html = e.fp.read()
        print 'error occured in opening url ' + html
        pass


def parseMainPage():
    def parseUl( ul ):
        result = {}
        for li in ul.findAll( 'li', recursive=False ):
            key = li.span.text
            url = li.a[ 'href' ]
            u = li.find( 'ul' )
            if u:
                result[ key ] = parseUl( u )
            else:
                result[ key ] = url
        return result

    url = "http://www.tubetamil.com"
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    soup = BeautifulSoup( html )
    div = soup.find( 'div', { 'id' : 'mainmenu' } )
    tubeIndex = parseUl( div.ul )
    print 'tube index', tubeIndex
    return tubeIndex

def thumb():
    xbmc.executebuiltin('Container.SetViewMode(500)')

def thumbnailView():
    xbmc.executebuiltin('Container.SetViewMode(500)')

def parseRadioPage():
    radioChannel = []
    try:
        response = urllib2.urlopen(LIVE_RADIO)
        xfile = response.read()
    except urllib2.HTTPError, e:
        xfile = e.fp.read()
        pass
    soup = BeautifulSoup( xfile )
    for channel in soup.findAll( 'channel' ):
        name = channel.title.text
        url = channel.link.text
        img = channel.thumbnail.text
        radioChannel.append( ( name, url, img ) )
    return radioChannel

def parseMoviePage( url ):
    print "movie:" + url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass

    srcRegex = '<h2 class="archive_title">\s*<a href="(.+?)".+?>(.+?)</a>'
    imgRegex = '<img src="(.+?)".*alt=""'
    navRegex = '<a class="pagi-next" href=\'(.+?)\'>'

    src = re.compile( srcRegex ).findall( html )
    img = re.compile( imgRegex ).findall( html )
    nav = re.compile( navRegex ).findall( html )

    return nav, zip( src, img )

#####================TAMIL TVs
def getTvLinks(url):
    tvChannel = {}
    response = net.http_GET( url )
    data = response.content
    elements = ET.fromstring(data)
    items = elements.findall('item')
    itemIndex = 0
    for item in items:
        itemName = item.find('title').text
        itemUrl = item.find('link').text
        itemImg = item.find('thumbnail').text
        nameImage = (itemName, itemImg)
        tvChannel[itemIndex] = (nameImage, itemUrl)
        itemIndex = itemIndex + 1
    return tvChannel

addonLocation = xbmc.translatePath(os.path.join('special://home', 'addons', addonId))
def get_pack(file):
    import hashlib
    return hashlib.md5(open(os.path.join(addonLocation,file)).read()).hexdigest()

def tvLink(url):
    tvLinks = getTvLinks(url)

    for index in range(len(tvLinks)):
        try:
            (name, img), url = tvLinks[index]
            url = url
            #print 'TV URL: ', url
            li = xbmcgui.ListItem(name , thumbnailImage=img)
            li.addStreamInfo('video', { 'Codec': 'h264', 'Width' : 1280 })
            contextMenu = []
            contextMenu.append(('Programe Guide','XBMC.RunPlugin(%s?mode=tvguide&name=%s)'%(sys.argv[0], urllib.quote_plus(name))))
            li.addContextMenuItems(contextMenu, replaceItems = True)

            #thumb()
            if 'giniko' in url:
                urlQuery = build_url({ 'mode' : 'giniko', 'url' : url, 'title' : name , 'iconImg' : img})
                #addon.add_directory( { 'mode' : 'giniko', 'url' : url, 'title' : name , 'iconImg' : img}, { 'title' : name}, img=img )
                xbmcplugin.addDirectoryItem(handle = addon_handle, url = urlQuery, listitem = li, isFolder = True)
            elif 'yupp' in url:
                urlQuery = build_url({ 'mode' : 'yupp', 'url' : url, 'title' : name , 'iconImg' : img})
                xbmcplugin.addDirectoryItem(handle = addon_handle, url = urlQuery, listitem = li, isFolder = True)
            else:
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        except:
            continue
    xbmcplugin.endOfDirectory(addon_handle)
    thumbnailView()

def GinikoURL(url, name, img):
    url = 'http://giniko.com/watch.php?id='+url.split('=', 1)[1]
    print url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    regex = 'file: "(.*?)"'
    playurl = re.compile( regex ).findall( html )
    print(playurl[0])

    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Opening stream ' + name)

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, thumbnailImage=img)
    playlist.add(playurl[0], listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def YuppURL(url, name, img):
    url = 'http://streams.yupptv.com/freechannelplayer.aspx?id='+url.split('=', 1)[1]
    print url
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    regex = "file:'(.+?)'"
    playurl = re.compile( regex ).findall( html )
    print(playurl[0])

    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Opening stream ' + name)

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, thumbnailImage=img)
    playlist.add(playurl[0], listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def tvGuide(name):
    update.TextBoxes(name + ' TV Schedule', 'TV Schedule')


######=======================END TAMIL TV



### CLODY CC FIX
def parseCustomURL(url):
    print 'log parse custom url ', url
    actualurl = url
    if 'cloudy' in url:
        r = re.search('(https?://(?:www\.|embed\.)cloudy\.(?:ec|eu|sx|ch|com))/(?:video/|embed\.php\?id=)([0-9a-z]+)', url)
        mediaid = r.group(2)
        actualurl = 'http://www.cloudy.ec/embed.php?id={0}'.format(mediaid)
    if 'videoraj' in url:
        r = re.search('(https?://(?:www\.|embed\.)videoraj\.(?:ec|eu|sx|ch|com))/(?:video/|embed\.php\?id=)([0-9a-z]+)', url)
        mediaid = r.group(2)
        actualurl = 'http://www.videoraj.sx/embed.php?id={0}'.format(mediaid)

    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    req = urllib2.Request(actualurl)
    r = opener.open(req)
    html = r.read()

    #print 'html ', html

    regex = 'key: "(.*?)"'
    res = re.compile(regex).findall(html)
    filekey = res[0]


    if 'cloudy' in url:
        apiurl = 'http://www.cloudy.ec/api/player.api.php?file={0}&key={1}'.format(mediaid, filekey)
    if 'videoraj' in url:
        apiurl = 'http://www.videoraj.sx/api/player.api.php?file={0}&key={1}'.format(mediaid, filekey)


    api_html = net.http_GET(apiurl).content
    rapi = re.search('url=(.+?)&title=', api_html)

    return urllib.unquote(rapi.group(1))



######========================

def parseRajMoviePage( url ):
    print "movie:" + url
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)

    try:
        req = urllib2.Request(url)
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass
    #print html

    srcRegex = '<div class="post-thumb">*\n<a href="(.+?)" title="(.+?)"'
    imgRegex = '<div class="post-thumb">*\n.*title.+?>*\n<img src="(.+?)".*alt="'
    #navRegex = '<a class=\'page-numbers\' href=\'(.+?)\?' #working
    navRegex = '<a class="next page-numbers" href="(.+?)(?:"|\?)'
    #class="next page-numbers" href="

    src = re.compile( srcRegex ).findall( html )
    img = re.compile( imgRegex ).findall( html )
    nav = re.compile( navRegex ).findall( html )[0]

    #print "src===>",img

    return nav, zip( src, img )


### Dailymotion Videos
### def get_media_url(self, host, media_id):

def get_daily_media_url(web_url):
    print 'web url: ' + web_url
    #print getDailyStreamUrl(web_url)
        link = net.http_GET(web_url).content
        if link.find('"error":') > 0:
            try:
                err_title = re.compile('"title":"(.+?)"').findall(link)[0]
                if not err_title:
                    err_title = 'Content not available.'

                err_message = re.compile('"message":"(.+?)"').findall(link)[0]
                if not err_message:
                    err_message = 'No such video or the video has been removed due to copyright infringement issues.'

                raise UrlResolver.ResolverError(err_message)
            except:
                pass

        imgSrc = ''
        matches = re.compile('"thumbnail_url":"(.+?)"').findall(link)

        if len(matches):
            imgSrc = matches[0]

        #common.addon.log('img:' + imgSrc)

        dm_live = re.compile('live_rtsp_url":"(.+?)"', re.DOTALL).findall(link)
        dm_1080p = re.compile('"1080"\:\[\{"type"\:".+?","url":"(.+?)"', re.DOTALL).findall(link)
        dm_720p = re.compile('"720"\:\[\{"type"\:".+?","url":"(.+?)"', re.DOTALL).findall(link)
        dm_high = re.compile('"480"\:\[\{"type"\:".+?","url":"(.+?)"', re.DOTALL).findall(link)
        dm_low  = re.compile('"380"\:\[\{"type"\:".+?","url":"(.+?)"', re.DOTALL).findall(link)
        dm_low2 = re.compile('"240"\:\[\{"type"\:".+?","url":"(.+?)"', re.DOTALL).findall(link)

        videoUrl = []

        if dm_live:
            liveVideoUrl = urllib.unquote_plus(dm_live[0]).replace("\\/", "/")
            liveVideoUrl = liveVideoUrl.replace("protocol=rtsp", "protocol=rtmp")
            liveVideoUrl = net.http_GET(liveVideoUrl).content
            videoUrl.append(liveVideoUrl)
        else:
            if dm_1080p:
                videoUrl.append(urllib.unquote_plus(dm_1080p[0]).replace("\\/", "/"))
            if dm_720p:
                videoUrl.append(urllib.unquote_plus(dm_720p[0]).replace("\\/", "/"))
            if dm_high:
                videoUrl.append(urllib.unquote_plus(dm_high[0]).replace("\\/", "/"))
            if dm_low:
                videoUrl.append(urllib.unquote_plus(dm_low[0]).replace("\\/", "/"))
            if dm_low2:
                videoUrl.append(urllib.unquote_plus(dm_low2[0]).replace("\\/", "/"))

        vUrl = ''
        vUrlsCount = len(videoUrl)
        if vUrlsCount > 0:
            q = '0'
            if q == '0':
                # Highest Quality
            print 'Highest quality'
                vUrl = videoUrl[0]
            elif q == '1':
                # Medium Quality
            print 'medium quality'
                vUrl = videoUrl[(int)(vUrlsCount / 2)]
            elif q == '2':
                # Lowest Quality
                vUrl = videoUrl[vUrlsCount - 1]

        #common.addon.log('url:' + vUrl)
    m_url = vUrl.split('?auth=')
    the_url = m_url[0] + '?redirect=0&auth=' + m_url[1]
    
    match = re.compile('(http://.+?.m3u8)', re.DOTALL).findall(net.http_GET(the_url).content)
    return match[0]

def parseDailymotion( url ):
   videos = []
   link = urllib2.urlparse.urlsplit( url )
   netloc = link.netloc
   path = link.path
   print 'daily start', netloc, path

   print "dailymotion url : " + url

   def parseDailymotionPlaylist( playlistId ):
      videos = []
      dlurl = 'https://api.dailymotion.com/playlist/' + playlistId + '/videos'
      try:
         response = net.http_GET( dlurl )
         html = response.content
      except urllib2.HTTPError, e:
         print "HTTPError : " + str( e )
         return videos

      jsonObj = json.loads( html )
      for video in jsonObj['list']:
         videos.append( 'http://www.dailymotion.com/' + str(video['id']) )
      return videos

   # Handle playlists
   playlistId = ''
   if 'jukebox' in url:
      playlistId = re.compile("\?list\[\]\=/playlist/(.+?)/").findall( url )[ 0 ]
   elif 'playlist' in url:
      playlistId = re.compile("playlist/(.+?)_").findall( url )[ 0 ]
   elif 'video/' in url:
      videoId = re.compile("video/(.+)").findall( path )[ 0 ]
      videoId = videoId.split( '_' )[ 0 ]
   elif 'swf' in url:
      videoId = re.compile("swf/(.+)").findall( path )[ 0 ]
   else:
      print "unknown dailymotion link"
      return videos

   if playlistId:
      print "playlistId : " + playlistId
      videos += parseDailymotionPlaylist( playlistId )
   else:
      videos += [ 'http://' + netloc + '/embed/video/' + videoId ]
   print 'dailymotion videos', videos
   return videos

def parseYoutube( url ):
   videos = []
   link = urllib2.urlparse.urlsplit( url )
   query = link.query
   netloc = link.netloc
   path = link.path

   print "youtube url : " + url

   def parseYoutubePlaylist( playlistId ):
      videos = []
      yturl = 'http://gdata.youtube.com/feeds/api/playlists/' + playlistId
      try:
         response = net.http_GET( yturl )
         html = response.content
      except urllib2.HTTPError, e:
         print "HTTPError : " + str( e )
         return videos

      soup = BeautifulSoup( html )

      for video in soup.findChildren( 'media:player' ):
         videoUrl = str( video[ 'url' ] )
         print "youtube video : " + videoUrl
         videos += parseYoutube( videoUrl )
      return videos

   # Find v=xxx in query if present
   qv = ''
   if query:
      qs = cgi.parse_qs( query )
      qv = qs.get( 'v', [''] )[ 0 ]
      if qv:
         qv = '?v=' + qv

   # Handle youtube gdata links
   playlistId = ''
   if re.search( '\?list=PL', url ):
      playlistId = re.compile("\?list=PL(.+?)&").findall( url )[ 0 ]
   elif re.search( '\?list=', url ):
      playlistId = re.compile("\?list=(.+?)&").findall( url )[ 0 ]
   elif re.search( '/p/', url ):
      playlistId = re.compile("/p/(.+?)(?:/|\?|&)").findall( url )[ 0 ]
   elif re.search( 'view_play_list', url ):
      plyalistId = re.compile("view_play_list\?.*?&amp;p=(.+?)&").findall( url)[ 0 ]

   if playlistId:
      print "playlistId : " + playlistId
      videos += parseYoutubePlaylist( playlistId )
   else:
      videos += [ 'http://' + netloc + path + qv ]
   return videos

def paerse_Hideplay( url ):
    html = open_url( url )
    link = re.compile( '"file":"(.*?)"' ).findall( html )
    return ( link[0] + '|referer=' + url )
    exit()

def Load_Video( url ):
   print "Load_Video=" + url
   try:
      response = urllib2.urlopen(url)
      html = response.read()
   except urllib2.HTTPError, e:
      html = e.fp.read()
      pass

   #html = net.http_GET( url ).content
   soup = BeautifulSoup( html )
   sourceVideos = []

   # Handle href tags
   for a in soup.findAll('a', href=True):
      if a['href'].find("youtu.be") != -1:
         sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

      if a['href'].find("youtube") != -1:
         sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

      if a['href'].find("dailymotion") != -1:
         sourceVideos.append('src="' + (a['href'].split()[0]) + ' ' +  ('width = ""'))

   # Handle embed tags
   #sourceVideos += re.compile( '<embed(.+?)>', flags=re.DOTALL).findall( html )

   # Handle iframe tags
   sourceVideos += re.compile( '<iframe(.+?)>').findall( html )

   # Handle Youtube new window
   src = re.compile( 'onclick="window.open\((.+?),' ).findall( html )
   if src:
      sourceVideos += [ 'src=' + src[ 0 ] ]

   if len( sourceVideos ) == 0:
      print "No video sources found!!!!"
      addon.show_ok_dialog( [ 'Page has unsupported video' ], title='Playback' )
      return

   videoItem = []
   for sourceVideo in sourceVideos:
      print "sourceVideo=" + sourceVideo
      sourceVideo = re.compile( 'src=(?:\"|\')(.+?)(?:\"|\')' ).findall( sourceVideo )[0]
      sourceVideo = urllib.unquote( sourceVideo )
      print "sourceVideo=" + sourceVideo
      link = urllib2.urlparse.urlsplit( sourceVideo )
      host = link.hostname
      host = host.replace( 'www.', '' )
      host = host.replace( '.com', '' )
      sourceName = host.capitalize()
      print "sourceName = " + sourceName

      if 'dailymotion' in host:
         sourceVideo = parseDailymotion( sourceVideo )
         for video in sourceVideo:
            print "sourceVideo : " + video
            #videoId = re.compile('dailymotion\.com/(.+)').findall( video )[ 0 ]
            #video = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=' + videoId
            videoItem.append( (video, sourceName, video ) )

      elif 'facebook' in host:
          print 'skip facebook host'
          continue

      elif 'youtube' in host:
         print 'Youtube source video before: ', sourceVideo
         sourceVideo = parseYoutube( sourceVideo )
         print 'Youtube source video after: ', sourceVideo
         for video in sourceVideo:
            print "sourceVideo : " + video
            hosted_media = urlresolver.HostedMediaFile( url=video, title=sourceName )
            if not hosted_media:
               print "Skipping video " + sourceName
               continue
            videoItem.append( (video, sourceName, hosted_media ) )
         print 'youtube video append : ', videoItem

      elif sourceVideo.endswith('.mp4') or sourceVideo.endswith('.flv'):
            videoItem.append((sourceVideo, sourceName, 'mp4|flv'))

        elif sourceName == 'Hideplay':
            videoItem.append( ( sourceVideo, 'GVideo|Hideplay', 'm3u8' ) )
  
      else:
         print "sourceVideo and Name : " + sourceVideo, sourceName
         hosted_media = urlresolver.HostedMediaFile( url=sourceVideo, title=sourceName )
         print 'hosted media : ', hosted_media
         if not hosted_media:
            print "Skipping video " + sourceName
            continue
         videoItem.append( (sourceVideo, sourceName, hosted_media ) )



   if len( videoItem ) == 0:
      addon.show_ok_dialog( [ 'Video does not exist' ], title='Playback' )
      exit()
   elif len(videoItem) == 1:
      url, title, hosted_media = videoItem[ 0 ]
      if 'dailymotion' in url:
            print 'dailymotion in url '
            stream_url = get_daily_media_url( url)
      else:
         stream_url = hosted_media.resolve()
      print "stream_url len=1 " + stream_url

      pDialog = xbmcgui.DialogProgress()
      pDialog.create('Opening stream ' + title)

      playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
      playlist.clear()
      listitem = xbmcgui.ListItem(title)
      playlist.add(stream_url, listitem)
      xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)
   else:
      partNo = 1
      prevSource = ''
      for sourceVideo, sourceName, _ in videoItem:
         if sourceName != prevSource:
            partNo = 1
            prevSource = sourceName

         title = sourceName + ' Part# ' + str( partNo )
         addon.add_video_item( { 'url' : sourceVideo }, { 'title' : title } )
         partNo += 1

      xbmcplugin.endOfDirectory(int(sys.argv[1]))

#####===TAMILGUN VIMEO ADD HTTP===###
def as_complex(dct):
    if '__complex__' in dct:
        return complex(dct['real'], dct['imag'])
    return dct
def parseVimeo(vimeovid):
   proxy_handler = urllib2.ProxyHandler({})
   opener = urllib2.build_opener(proxy_handler)
   if 'http' in vimeovid:
       vimeovid = vimeovid.replace('https', 'http')
       vimeovid = vimeovid
   else:
       vimeovid = 'http:'+vimeovid
   vimeoid = vimeovid.split('/video/')[1]
   print "Load_vimeo Video = " + vimeovid
   print "vimeo id=: ", vimeoid
   try:
      req = urllib2.Request(vimeovid)
      req.add_header('Referer', 'http://vimeo.com/'+vimeoid)
      response = urllib2.urlopen(req)
      html = response.read()
   except urllib2.HTTPError, e:
      html = e.fp.read()
      pass
   #print html

   movieregex = '"hls".*"hd":"(.*?)"'
   #movieregex = '"hls":{"url":"(.*?)"'
   #movieregex = '"hd":{"profile":113,"origin":"gcs","url":"(.*?)"'
   #movieregex = 'var t=(.*?);if\(!t.request\)'
   movieregex = '"url":"(.*?)"'
   vimeovideo = re.compile( movieregex ).findall( html )
   print 'vimeo video string: ', vimeovideo
   #jsonstr = json.dumps(vimeovideo)
   #print json.loads(jsonstr)
   #exit()

   if len(vimeovideo) == 1:
      print 'lenth if ->'
      return vimeovideo[0]
   else:
      movieregex = '"url":"(.*?)"'
      print movieregex
      vimeovideo = re.compile( movieregex ).findall( html )
      print 'vimeo video length', len(vimeovideo),vimeovideo
      if len(vimeovideo) > 1:
          return vimeovideo[2]
      else:
          return vimeovideo

import string
digs = string.digits + string.letters

def int2base(x, base):
    if x < 0: sign = -1
    elif x == 0: return digs[0]
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def unpack(p, a, c, k, e=None, d=None):
    ''' unpack
    Unpacker for the popular Javascript compression algorithm.

    @param  p  template code
    @param  a  radix for variables in p
    @param  c  number of variables in p
    @param  k  list of c variable substitutions
    @param  e  not used
    @param  d  not used
    @return p  decompressed string
    '''
    # Paul Koppen, 2011
    for i in xrange(c-1,-1,-1):
        if k[i]:
            p = re.sub('\\b'+int2base(i,a)+'\\b', k[i], p)
    return p

def parseCyberCustom(url):


    if 'toolstube' in url:
        api_html = net.http_GET(url).content
        rapi = re.search('var files = \'{".*":"(.+?)"}', api_html)
        print 'this is ------------------ toolstube',
        return urllib.unquote(rapi.group(1)).replace('\\/', '/')+'|Referer=http://toolstube.com/'

    if 'playhd.video' in url:
        api_html = net.http_GET(url).content
        rapi = re.search('source src="(.+?)" type=\'video/mp4\'', api_html)
        reg1 = 'source src="(.+?)" type=\'video/mp4\''
        playurl = re.compile(reg1).findall( api_html )
        print 'this is ------------------ playhd', playurl
        print 'non'
        #return rapi.group(1)+'|Referer=http://www.playhd.video/embed.php?'
        return playurl[0]+'|Referer=http://www.playhd.video/embed.php?'

    if 'mersalaayitten.com' in url:
        #http://mersalaayitten.com/media/nuevo/econfig.php?key=1639
        id = url.split('/embed/')[1]
        newUrl = 'http://mersalaayitten.com/media/nuevo/econfig.php?key='+id
        #"http://mersalaayitten.com/media/nuevo/player.swf"
        api_html = net.http_GET(newUrl, headers={'Referer':'http://mersalaayitten.com/media/nuevo/player.swf'}).content
        print 'api_html', api_html
        rapi = re.search('<html5>(.*?)</html5>', api_html)
        return rapi.group(1)
        print 'mersalayitten id='+id
    if 'googleplay' in url:
        api_html = net.http_GET(url).content
        reg1 = '<source src="(.*?)" type="video/mp4"'
        videourl = re.compile(reg1).findall( api_html )[0]
        return videourl+'|Referer=http://googleplay.tv'
    if 'fastplay' in url:
        api_html = net.http_GET(url).content
        fastReg1 = '\|\|div\|vvad\|(.*?)\|'
        fastReg2 = '\|mp4\|(.*?)\|'
        doplay = re.compile(fastReg1).findall( api_html )[0]
        vhash = re.compile(fastReg2).findall( api_html )[0]
        return 'http://'+doplay+'.fastplay.sx/'+vhash+'/v.mp4|Referer=http://fastplay.sx'
    if 'megamp4' in url:
        api_html = net.http_GET(url).content
        if not api_html == 'File was deleted':
            evalreg = "javascript'>(.*?)\n"
            s = re.compile(evalreg).findall( api_html )[0]
            js = eval('unpack' + s[s.find('}(')+1:-1])
            moviereg = 'file:"(.*?)"'
            movieurl = re.compile(moviereg).findall( js )[0]
            return movieurl
        else:
            print "megamp4 file deleted"
            return False
    if 'hideplay' in url:
        return paerse_Hideplay( sourceVideo )




#####===TAMILGUN MOVIES===#####

def parseGunMoviePage( url ):
   proxy_handler = urllib2.ProxyHandler({})
   opener = urllib2.build_opener(proxy_handler)
   print 'GUN URL: ',url

   try:
      req = urllib2.Request(url)
      opener.addheaders = [('User-agent', 'Mozilla/5.0')]
      r = opener.open(req)
      html = r.read()
   except urllib2.HTTPError, e:
      html = e.fp.read()
      pass

   srcRegex = '<a href="(.+?)"><img width=".*" height="(?:150|1)" src='
   imgRegex = '><img width=".*" height="(?:150|1)" src="(.+?)" class'
   titleRegex = '<h3><a href=.*">(.+?)</a>'
   navRegex = '<li class="next"><a href="(.+?)">'

   src = re.compile( srcRegex ).findall( html )
   img = re.compile( imgRegex ).findall( html )
   nav = re.compile( navRegex ).findall( html )
   title = re.compile(titleRegex).findall(html)
   src = zip( src, title)
   #print 'src gun movie',img

   return nav, zip( src, img )


def Load_GunVideo( url, iconImg , secrun = ''):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    print 'Load_GunVideo: ',url

    try:
        req = urllib2.Request(url)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        r = opener.open(req)
        html = r.read()
    except urllib2.HTTPError, e:
        html = e.fp.read()
        pass


    sourceVideos = []

    try:
        iframe = re.compile('(?:iframe src|IFRAME SRC)="(.+?)"').findall(html)[0]
        print "iframe===>>",iframe

        try:
             req = urllib2.Request(iframe)
             req.add_header('Referer', 'http://tamilgun.com')
             html2 = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
             html2 = e.fp.read()
             pass

        moviefile = re.compile("file:'(.*?)'").findall(html2.read())
        print "Movie FIle", moviefile
        sourceVideos += moviefile
    except:
        print 'iframe skipped'
        pass

    #html = net.http_GET( url ).content
    soup = BeautifulSoup( html )
    #print 'html',html

    # Handle href tags
    for a in soup.findAll('a', href=True):
        if a['href'].find("youtu.be") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("playhd.video") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("player.vimeo.com") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("cloudy.ec") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
        if a['href'].find("mersalaayitten.com") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("youtube") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')

        if a['href'].find("dailymotion") != -1:
            sourceVideos.append('src="' + (a['href'].split()[0]) + ' ' +  ('width = ""'))
        if secrun == '':
            if a['href'].find("view_video.php") != -1:
                #sourceVideos.append('src="' + (a['href'].split()[0]) + '" ')
                url1 = a['href'].split()[0]
                if 'vdogun.com' in url1:
                    print 'log: found vdogun url1 ', url1
                    sourVideo = Load_GunVideo(url1, iconImg, 'secrun')
                    print 'getmovie url', sourVideo
                    x = sourVideo
                    sourceVideos.append(x)
                    print 'log: running after vdogun '

    # Handle embed tags
    #sourceVideos += re.compile( '<embed(.+?)>', flags=re.DOTALL).findall( html )

    #iframe videowraper
    #videoWrapper = 'class="videoWrapper player">.*<iframe src="(.+?)"'
    mp4Video = re.compile('file: \'(.*?)\'').findall( html )
    #sourceVideos.append(re.compile('file: \'(.*?)\''))
    sourceVideos += re.compile('file: \'(.*?)\'').findall( html )
    sourceVideos += re.compile('file:\'(.*?)\'').findall( html )
    sourceVideos += re.compile('file:"(.*?)"').findall( html )
    sourceVideos += re.compile('"file":"(.*?)"').findall( html )
    sourceVideos += re.compile('type="video/mp4" src="(.*?)"').findall( html )
    print 'print sourcevideos', sourceVideos
    #file:'http://vod.zecast.net/tamilgun/mp4:budhan.mp4/playlist.m3u8'type="video/mp4"

    # Handle iframe tags
    #sourceVideos += re.compile( videoWrapper).findall( html )
    sourceVideos += re.compile( '<(?:iframe|IFRAME)(.+?)>').findall( html )

    sourceVideos += re.compile( '<source(.+?)>').findall( html )

    sourceVideos += re.compile( '<video.*src="(.+?)">').findall( html )
    print 'source videos',sourceVideos

    # Handle Youtube new window
    src = re.compile( 'onclick="window.open\((.+?),' ).findall( html )
    if src:
        sourceVideos += [ 'src=' + src[ 0 ] ]

    if len( sourceVideos ) == 0:
        print "No video sources found!!!!"
        addon.show_ok_dialog( [ 'Page has unsupported video' ], title='Playback' )
        return

    videoItem = []
    for sourceVideo in sourceVideos:
        print "sourceVideo=" + sourceVideo
        sourceVideo = sourceVideo.replace('\/', '/')
        try:
            sourceVideo = re.compile( '(?:src|SRC)=(?:\"|\')(.+?)(?:\"|\')' ).findall( sourceVideo )[0]
            sourceVideo = urllib.unquote( sourceVideo )
        except:
            sourceVideo = sourceVideo
        print "sourceVideo=" + sourceVideo
        sourceVideo = sourceVideo.replace('nowvideo.co', 'nowvideo.ch')
        link = urllib2.urlparse.urlsplit( sourceVideo )
        host = link.hostname
        try:
            host = host.replace( 'www.', '' )
            host = host.replace( '.com', '' )
            sourceName = host.capitalize()
            print "sourceName = " + sourceName
        except:
            pass
            host = ''

        if 'dailymotion' in host:
            sourceVideo = parseDailymotion( sourceVideo )
            for video in sourceVideo:
                print "sourceVideo : " + video
                videoId = re.compile('dailymotion\.com/(.+)').findall( video )[ 0 ]
                video = 'plugin://plugin.video.dailymotion_com/?mode=playVideo&url=' + videoId
                print 'Dailymotion parsed video:', video
                videoItem.append( (video, sourceName, video ) )

        if 'Tamilgun' in sourceName:
            videoItem.append( ((sourceVideo+'|Referer='+url), sourceName, 'ToolsTube' ) )

        if 'facebook' in host:
            print 'skip facebook iframe'
            pass

        elif 'youtube' in host:
            sourceVideo = parseYoutube( sourceVideo )
            for video in sourceVideo:
                print "sourceVideo : " + video
                hosted_media = urlresolver.HostedMediaFile( url=video, title=sourceName )
                if not hosted_media:
                    print "Skipping video " + sourceName
                    continue
                videoItem.append( (video, sourceName, hosted_media ) )

        elif 'vimeo' in host:
            print 'source video vimeo: ', sourceVideo
            vimeovideo = parseVimeo(sourceVideo)
            print 'vimeo video ==> ', vimeovideo
            if vimeovideo:
                videoItem.append( (vimeovideo, sourceName, vimeovideo ) )
            print 'log vid item',videoItem

        elif 'toolstube' in host:
            print 'toolstube found'
            videoItem.append( (parseCyberCustom(sourceVideo), sourceName, 'ToolsTube' ) )

        elif 'mersalaayitten' in host:
            print 'hello mersal'
            videoItem.append( (parseCyberCustom(sourceVideo), sourceName, 'Mersal' ) )

        elif 'fastplay' in host:
            print 'Fast play in host'
            videoItem.append( (parseCyberCustom(sourceVideo), sourceName, 'Fastplay' ) )
        elif 'megamp4' in host:
            print 'Megamp4 in host'
            videoItem.append( (parseCyberCustom(sourceVideo), sourceName, 'MegaMP4' ) )


        elif 'playhd.video' in sourceVideo:
            print 'hello playhd'
            if sourceVideo.endswith('.mp4'):
                videoItem.append((sourceVideo, sourceName, 'mp4'))
            else:
                purl = parseCyberCustom(sourceVideo)
                videoItem.append( (purl, sourceName, 'playhd' ) )
                print 'log: playhd catched', purl
        elif 'googleplay.tv' in sourceVideo:
            videoItem.append( (parseCyberCustom(sourceVideo), sourceName, 'googleplay' ) )


        elif sourceVideo.endswith('.mp4'):
            if secrun != '':
                return sourceVideo
            else:
                videoItem.append((sourceVideo, sourceName, 'mp4'))

        elif sourceVideo.endswith('.m3u8'):
            if secrun != '':
                return sourceVideo
            else:
                videoItem.append((sourceVideo, sourceName, 'm3u8'))

        else:
            print "sourceVideo else: " + sourceVideo
            hosted_media = urlresolver.HostedMediaFile( url=sourceVideo, title=sourceName )
            if not hosted_media:
                print "Skipping video " + sourceName
                continue
            videoItem.append( (sourceVideo, sourceName, hosted_media ) )


    print 'videoitem lenth : ' + str(len(videoItem))
    if len( videoItem ) == 0:
        addon.show_ok_dialog( [ 'Video does not exist' ], title='Playback' )
    elif len(videoItem) == 1:
        url, title, hosted_media = videoItem[ 0 ]
        print 'video item array: ', videoItem[0]
        if 'dailymotion' in url:
            stream_url = url
        elif 'Player.vimeo' == title:
            if not url:
                addon.show_ok_dialog( [ 'Video does not exist' ], title='Playback' )
            else:
                print 'vimeo url: ', len(url[0])
                if len(url[0]) < 5:
                    stream_url = url
                else:
                    stream_url = url[0]
                title = 'Vimeo Video'
                print 'im vimeo video: ', stream_url
        elif url.endswith('.mp4'):
            stream_url = url
        elif url.endswith('.m3u8'):
            stream_url = url
        elif 'cloudy' in url:
            print 'in cloudy gun'
            stream_url = parseCustomURL(url)
        elif 'videoraj' in url:
            print 'in videoraj gun'
            stream_url = parseCustomURL(url)
        elif 'grab.php' in url:
            print 'in tamilgun google video', url
            stream_url = url
        elif 'play.php' in url:
            print 'in tamilgun play php google video', url
            stream_url = url
        elif 'playhd.video' in url:
            stream_url = url
        else:
            hosted_media = urlresolver.HostedMediaFile( url=url, title=sourceName )
            surl = hosted_media.resolve()
            if surl != False:
                stream_url = surl
            else: pass
            print 'im in hostedmedia else'
        #print "stream_url " + stream_url

        print 'icon img: ', iconImg

        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Opening stream ' + title)

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        listitem = xbmcgui.ListItem(title, thumbnailImage=iconImg)
        playlist.add(stream_url, listitem)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)
    else:
        partNo = 1
        prevSource = ''
        for sourceVideo, sourceName, hostname in videoItem:
            if sourceName != prevSource:
                partNo = 1
                prevSource = sourceName

            title = sourceName + ' Part# ' + str( partNo )
            print 'icon=====>',iconImg
            addon.add_video_item( { 'url' : sourceVideo }, { 'title' : title } , img=iconImg, fanart=iconImg)
            partNo += 1

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Gun_Movie_Main( url ):
    #print "main_movie:" + url
    nav, link = parseGunMoviePage( url )
    #print "nav => ",nav[0]

    for ( page, title ), img in link:
        try:
            title =  addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            pass
        thumb()
        if not "http://" in img:
            img = "http:"+img
        #print 'tamilgun img: ', img
        addon.add_directory( { 'mode' : 'load_gunvideos', 'url' : page , 'iconImg' : img}, { 'title' : title }, img=img, total_items=len(link) )
    if nav:
        addon.add_directory( { 'mode' : 'gunmovie', 'url' : nav[0] }, { 'title' : '[B]Next Page...[/B]' }, img="https://lh3.googleusercontent.com/-NsVeHCUW0lo/V4b8r67FVSI/AAAAAAAAD7U/G1ifDqs0nFENPck0-oKCQgc3-Gdm_JM7QCCo/s574/next_574x358.png" )

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()
#####===END OF TAMILGUN===#####

def Main_Categories():

    addon.add_directory( { 'mode' : 'tv' }, { 'title' : '[B]Live TV[/B]' },
                        img='https://lh3.googleusercontent.com/-z2m9btbtufU/VTBYMr2SQjI/AAAAAAAACQg/XI5T2i4RAgg/s300-Ic42/tv_tamil.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'gunmovie', 'url' : TAMIL_GUN_HD }, { 'title' : '[B]HD Movies - TamilGun[/B]' },
                        img='https://lh3.googleusercontent.com/-H5GL4O0J95s/VTBYJXyNY9I/AAAAAAAACRQ/6Xnv1fAwrfY/s300-Ic42/tamilmovies_tamilgun.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'leaf', 'url' : 'http://www.tubetamil.com/category/watch-cinema-videos/watch-new-movie-trailers'  }, { 'title' : '[B]Tamil Trailers[/B]' },
                        img=getImgPath('Movie Trailers') )
    addon.add_directory( { 'mode' : 'leaf_bw', 'url' : 'http://behindwoods.com/tamil-movies/tamil-trailers.html'  }, { 'title' : '[B]Behindwoods Trailers[/B]' },
                        img=getImgPath('Movie Trailers') )
    addon.add_directory( { 'mode' : 'leaf', 'url' : 'http://www.tubetamil.com/category/watch-daily-tamil-news-online'  }, { 'title' : '[B]Tamil News[/B]' },
                        img=getImgPath('News') ) 
    addon.add_directory( { 'mode' : 'sportstv' }, { 'title' : '[B]Sports TV[/B]' },
                        img='https://lh3.googleusercontent.com/-BDHqgEO-9LU/VTBYMV5dBtI/AAAAAAAACQc/6m7Ueu_47LE/s300-Ic42/tv_sports.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'linksakash' }, { 'title' : '[B]Indian TV[/B]' },
                        img='https://lh3.googleusercontent.com/--XYDZL0rZg0/VTBYLZjVYcI/AAAAAAAACQY/eCc6qwHJ3zI/s300-Ic42/tv_other.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'radio' }, { 'title' : '[B]Live Radio[/B]' },
                        img='https://lh3.googleusercontent.com/-uD5U4HlupNk/VTBYKKWHmdI/AAAAAAAACRE/2rgwS4HgFwU/s300-Ic42/tamilradios.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'vod' }, { 'title' : '[B]On Demand[/B]' },
                        img='https://lh3.googleusercontent.com/-VlNVsGLYeUQ/VTBYCl4O7SI/AAAAAAAACOE/1V63u_Ax6EQ/s300-Ic42/ondemand_tubetamil.png',
                        fanart=fanartimg )
    #addon.add_directory( { 'mode' : 'movie', 'url' : MOVIE_URL }, { 'title' : '[B]Movies[/B]' },
                        #img=getImgPath('Movies') )
    addon.add_directory( { 'mode' : 'vijayVOD', 'url' : vijayVODUrl }, { 'title' : '[B]Vijay TV Video ONDEMAND[/B]' },
                        img='https://lh3.googleusercontent.com/-_fO6wmIeejo/VjW5tvmbj7I/AAAAAAAAClY/l0GliGBEEm4/s300-Ic42/hotstar.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'rajshows', 'url' : raj_vijay_serial }, { 'title' : '[B]Vijay TV Serials[/B]' },
                        img='https://lh3.googleusercontent.com/-1emFcwTbPT4/VTBYEiecdfI/AAAAAAAACOY/nRL_v6cMP9I/s300-Ic42/serials.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'rajshows', 'url' : raj_vijay_shows }, { 'title' : '[B]Vijay TV Shows[/B]' },
                        img='https://lh3.googleusercontent.com/-j5Uw-l9pfnY/VTBYDmMd-TI/AAAAAAAACOQ/EIYBy3SuYO4/s300-Ic42/other_shows.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'einthusan', 'url' : EINTHUSAN }, { 'title' : '[B]Einthusan[/B]' },
                        img='https://lh3.googleusercontent.com/-V0sr2aR40lA/VjW3Z4zHcZI/AAAAAAAAClM/G7iXP0Xrhw4/s300-Ic42/einthusan.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'rajmovie', 'url' : MOVIE_RAJ_URL }, { 'title' : '[B]Movies - Raj[/B]' },
                        img='https://lh3.googleusercontent.com/-D9l_X6D0Fp0/VTBYHBgDB0I/AAAAAAAACPE/npl7vo6x_-Q/s300-Ic42/tamilmovies_rajtamil.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'gunmovie', 'url' : MOVIE_GUN_MOVI }, { 'title' : '[B]Movies - TamilGun[/B]' },
                        img='https://lh3.googleusercontent.com/-H5GL4O0J95s/VTBYJXyNY9I/AAAAAAAACRQ/6Xnv1fAwrfY/s300-Ic42/tamilmovies_tamilgun.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'settings' }, { 'title' : '[B]Settings[/B]' },
                        img='https://lh3.googleusercontent.com/-XmQchEnyeWs/VTBYFAUm6_I/AAAAAAAACOs/AfaY71aUFz0/s300-Ic42/settings.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'iconupdate' }, { 'title' : '[B]Icon Update[/B]' },
                        img='https://lh3.googleusercontent.com/-gRUvJDPR-c4/VTBYKSztq-I/AAAAAAAACQA/02AGuBxxlvc/s300-Ic42/thumbnail_update.png',
                        fanart=fanartimg )
    addon.add_directory( { 'mode' : 'notice' }, { 'title' : '[B]Notice[/B]' },
                        img='https://lh3.googleusercontent.com/-prtKEs8JOqw/VTBYBu0xkPI/AAAAAAAACNs/WqirXLIa8KI/s300-Ic42/notice.png',
                        fanart=fanartimg )
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()

def Vod_Main():
   print "main_vod"
   tubeIndex = cache.cacheFunction( parseMainPage )
   print "size = ", len(repr(tubeIndex))
   #print 'TubeIndex:'
   #pprint(tubeIndex, width=1)

   for key, value in sorted( tubeIndex.items() ):
      if key == 'Comedy':
         mode = 'leaf'
         path = value
      elif type( value ) != dict:
         continue
      else:
         mode = 'tree'
         path = key
      addon.add_directory( { 'mode' : mode, 'url' : path }, { 'title' : '[B]%s[/B]' % key },
                           img=getImgPath(key) )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

def Movie_Main( url ):
   print "main_movie:" + url
   nav, link = parseMoviePage( url )

   for ( page, title ), img in link:
      title =  addon.unescape(title)
      title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
      addon.add_directory( { 'mode' : 'load_videos', 'url' : page }, { 'title' : title },
                           img=img, total_items=len(link) )
   if nav:
      addon.add_directory( { 'mode' : 'movie', 'url' : nav[0] }, { 'title' : '[B]Next Page...[/B]' } )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

def Raj_Movie_Main( url ):
    print "main_movie:" + url
    nav, link = parseRajMoviePage( url )
    #print 'print link => '
    #print link #edit

    print 'Navigation ==> ',nav
    index = 1
    for ( page, title ), img in link:
        if index == 2 or index == 3:
            stitle = 'test'
        try:
            title =  addon.unescape(title).encode('utf8', 'ignore')
        except UnicodeDecodeError:
            title = 'Unicodechar'
            pass
        title = title.replace('Watch ', '', 1)
        title = title.replace(' Movie Online', '', 1)
        title = title.replace(' movie online', '', 1)
        #print "title =>> ",title
        #title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
        #title = title.encode('ascii', 'ignore')
        #print 'image================>',img
        index = index + 1
        thumb()
        addon.add_directory( { 'mode' : 'load_gunvideos', 'url' : page , 'iconImg' : img}, { 'title' : title }, img=img, total_items=len(link) )
    if nav:
        addon.add_directory( { 'mode' : 'rajmovie', 'url' : nav }, { 'title' : '[B]Next Page...[/B]' } )

    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    thumbnailView()



def Raj_Shows( url ):
   print "main_movie:" + url
   nav, link = parseRajMoviePage( url )
   #print 'print link => '
   #print link #edit

   print 'Navigation ==> ',nav

   for ( page, title ), img in link:
      try:
         title =  addon.unescape(title).encode('utf8', 'ignore')
      except UnicodeDecodeError:
         pass
      title = title.replace('Watch ', '', 1)
      title = title.replace(' Movie Online', '', 1)
      title = title.replace(' movie online', '', 1)
      #print "title =>> ",title
      #title = unicodedata.normalize('NFKD', unicode(title)).encode('ascii', 'ignore')
      #title = title.encode('ascii', 'ignore')
      thumb()
      addon.add_directory( { 'mode' : 'load_videos', 'url' : page }, { 'title' : title }, img=img, total_items=len(link) )
   if nav:
      addon.add_directory( { 'mode' : 'rajmovie', 'url' : nav }, { 'title' : '[B]Next Page...[/B]' } )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()


def Main_Tree( url ):
   print "tree:" + url + ":"
   tubeIndex = cache.cacheFunction( parseMainPage )
   path = url.split( '&' )
   for key in path:
      tubeIndex = tubeIndex[ key ]

   for key, value in sorted( tubeIndex.items() ):
      if type( value ) != dict:
         mode = 'leaf'
         path = value
      else:
         mode = 'tree'
         path = url + '&' + key
      addon.add_directory( { 'mode' : mode, 'url' : path }, { 'title' : '[B]%s[/B]' % key },
                           img=getImgPath( key ) )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

def Main_Leaf( url ):
   print "leaf:" + url
   response = net.http_GET( url )
   html = response.content
   soup = BeautifulSoup( html )
   div = soup.findAll( 'div', { 'class' : 'video' } )
   for d in div:
      video = d.find( 'div', { 'class' : 'thumb' } )
      url = video.a[ 'href' ]
      title = video.a[ 'title' ]
      img = video.img[ 'src' ]

      addon.add_directory( { 'mode' : 'load_videos', 'url' : url }, { 'title' : title.encode('utf-8')},
                           img=img, total_items=len(div) )

   pages = soup.find( 'ul', { 'class' : 'page_navi' } )
   nextPage = pages.find( 'li', { 'class' : 'next' } )
   if nextPage:
      nextPageUrl = nextPage.a[ 'href' ]
      addon.add_directory( { 'mode' : 'leaf', 'url' : nextPageUrl }, { 'title' : '[B]Next Page...[/B]' } )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

def Main_Leaf_bw( url ):
   print "leaf:" + url
   response = net.http_GET( url )
   html = response.content
   soup = BeautifulSoup( html )
   div = soup.findAll( 'a', { 'class' : 'img-loader-cntr' } )
   print "div =>> ",div
   for a in div:
      url = 'http://behindwoods.com' + a[ 'href' ]
      title = a[ 'title' ]
      img = 'http://behindwoods.com' + a.img[ 'src' ]

      addon.add_directory( { 'mode' : 'load_videos', 'url' : url }, { 'title' : title.encode('utf-8')},
                           img=img, total_items=len(div) )

   pages = soup.find( 'ul', { 'class' : 'page_navi' } )
   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

########========AFTER UPDATE
def checkupdate():
    Main_Categories()

def viewNotice():
    update.TextBoxes("[B][COLOR green]Tamil KODI Notice[/B][/COLOR]", update.getNotice())

def iconUpdate():
    pass
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('TamilKODI', 'Do you want to update icons?')
    print 'return value:', str(ret)
    if ret:
        print 'return value true'
        url = 'http://cyberrule.com/tv/tamilkodi/get.php?icon'
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        req = urllib2.Request(url)
        r = opener.open(req)
        the_page = r.read()

        regex = '<image>url="(.*?)"</image>'
        ver = re.compile(regex).findall(the_page)

        print 'version length: ', len(ver)
        value = 100/len(ver)
        index = 1
        print 'value = ', value
        pDialog = xbmcgui.DialogProgress()
        progres = pDialog.create('Icon Update', 'Initializing downlaod...')


        for url in ver:
            print 'percentage: ', (value*index)
            pDialog.update((value*index), 'Downloading images...')
            name = url.split('/')[-1]
            name = name.replace('%20', ' ')
            print 'image name: ', name, url
            if 'icon.png' in name:
                update.copyFile(os.path.abspath(programPath + "/" + name), openFile(url))
                print 'log: copying image: ' + str(name)
            else:
                update.copyFile(os.path.abspath(programPath + "/resources/images/" + name), openFile(url))
                print 'log: copying icon image: ' + str(name)

            index += 1

        xbmc_texture_path = os.path.join(xbmc.translatePath('special://home'), 'userdata/Database/Textures13.db')
        if progres:
            print 'progress true'
        else:
            print 'progress false'

        try:
            time.sleep(3)
            os.remove(xbmc_texture_path)
            addon.show_ok_dialog( [ 'Please Restart XBMC/KODI' ], title='Thumbnail Cache Removed' )
            print 'im done'
        except:
            pass
    else:
        print 'return value false'
    '''


    '''

def openFile(url):
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    req = urllib2.Request(url)
    r = opener.open(req)
    the_page = r.read()
    return the_page

def TV_Main():
   print "tv_main"
   tvIndex = parseTvPage()

   for key, value in sorted( tvIndex.items() ):
      if type( value ) != dict:
         continue
      else:
         mode = 'tv_tree'
         path = key
      addon.add_directory( { 'mode' : mode, 'url' : path }, { 'title' : '[B]%s[/B]' % key },
                           img=getImgPath(key) )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))

def Radio_Main():
   print "radio_main"
   radioIndex = parseRadioPage()

   for (name, url, img) in radioIndex:
      url = name + '|' + url
      addon.add_directory( { 'mode' : 'tv_leaf', 'url' : url }, { 'title' : '[B]%s[/B]' % name },
                           img=img, total_items=len(radioIndex) )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))
   thumbnailView()

def TV_Tree( url ):
   print "TV_Tree" + url
   tvIndex = parseTvPage()
   path = url.split( '&' )
   for key in path:
      tvIndex = tvIndex[ key ]

   for key, value in sorted( tvIndex.items() ):
      if type( value ) != dict:
         mode = 'tv_leaf'
         (path,img) = value
         path = key + '|' + path
      else:
         mode = 'tv_tree'
         path = url + '&' + key
      addon.add_directory( { 'mode' : mode, 'url' : path },
                           { 'title' : '[B]%s[/B]' % key },
                           img=img )

   xbmcplugin.endOfDirectory(int(sys.argv[1]))

def TV_Leaf( url ):
   print "TV_Leaf:" + url
   sep = url.split( '|' )
   title = sep[ 0 ]
   stream_url = sep[ 1 ]
   pDialog = xbmcgui.DialogProgress()
   pDialog.create('Streaming ' + title )

   playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
   playlist.clear()
   listitem = xbmcgui.ListItem( title )
   playlist.add(stream_url, listitem)
   xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
name = addon.queries.get('name', None)
play = addon.queries.get('play', None)
title = addon.queries.get('title', None)
iconImg = addon.queries.get('iconImg', None)

print "MODE: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "play: "+str(play)
print "arg1: "+sys.argv[1]
print "arg2: "+sys.argv[2]
print 'arg length: ', len(sys.argv)

if play:
   print 'log: in play section', url
   stream_url = None
   if 'dailymotion' in url:
      stream_url = get_daily_media_url(url)
   elif 'vimeocdn' in url:
      stream_url = url
   elif 'toolstube' in url:
       print 'log: toolstube true'
       stream_url = url+'|Referer=http://toolstube.com/player/embed_player.php'
   elif 'playhd.video' in url:
       print 'log: playhd.video play'
       stream_url = url+'|referer='+url
   elif url.endswith('mp4'):
       stream_url = url
   elif url.endswith('m3u8'):
       stream_url = url
   elif 'cloudy' in url:
       pass
       stream_url = parseCustomURL(url)
   elif 'videoraj' in url:
       stream_url = parseCustomURL(url)
   elif 'play.php' in url:
            print 'in tamilgun play php google video', url
            stream_url = url
   elif 'fastplay' in url:
        print 'in fastplay ', url
        stream_url = url
   elif 'hideplay' in url:
        stream_url = paerse_Hideplay( url )
   else:
      print 'URL NEW: ', url
      hosted_media = urlresolver.HostedMediaFile( url=url, title=name )
      print "hosted_media"
      print hosted_media
      if hosted_media:
         stream_url = hosted_media.resolve()
         print 'stream url', stream_url

   if stream_url:
      print 'stream url true', stream_url
      xbmcplugin.setResolvedUrl(addon_handle, True,
                                      xbmcgui.ListItem(path=stream_url))
      #addon.resolve_url(stream_url)
   else:
      print "unable to resolve"
      addon.show_ok_dialog( [ 'Unknown hosted video' ], title='Playback' )
else:

    if mode == 'main':
        try:
            checkupdate() ##check update and display main categories
        except:
            xbmc.executebuiltin("XBMC.Notification(TamilKodi Notification,Error while checking update,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")

    elif mode == 'notice':
       viewNotice()

    elif mode == 'iconupdate':
       iconUpdate()

    elif mode == 'radio':
       #Radio_Main()
       tvLink(LIVE_RADIO)

    elif mode == 'vod':
       Vod_Main()

    elif mode == 'vijayVOD':
        try:
            print 'Log: import success', url
            from resources.specials import *
            isDirectory = addon.queries.get('isDirectory', None)
            vijayVOD(url, mode, isDirectory)
        except:
            try:
                dialog = xbmcgui.Dialog()
                dialog.ok("Loading at first time", "Downloading necessary files. Won't be shown next time.")
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), '__init__.py')
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'specials.py')
                xbmc.executebuiltin("XBMC.Notification(TamilKodi Notification,Vijay TV Ondemand Loaded,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")
            except:
                xbmc.executebuiltin("XBMC.Notification(TamilKodi Error,Vijay VOD Import failed,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")
                #        return control.infoDialog('You need to set your download folder in addon settings first', 'File Not Downloadable')

    elif mode == 'einthusan':

        try:

            from resources.einthusan import *
            print 'Log: einthusan import success'
            isDirectory = addon.queries.get('isDirectory', None)
            #einthusan(url, mode, isDirectory)
            print 'inthusan', get_pack('resources/einthusan.py')
            if '08ef89ec30c583d67a2aadd364872b0a' != get_pack('resources/einthusan.py'):
                getdov

            params=get_params()
            url=''
            name=''
            submode=0
            language=''

            try:
                url=urllib.unquote_plus(params["url"])
            except:
                pass

            try:
                name=urllib.unquote_plus(params["name"])
            except:
                pass

            try:
                submode=int(params["submode"])
                print 'submode value: '+submode
            except:
                pass

            try:
                language=urllib.unquote_plus(params["lang"])
            except:
                pass

            function_map = {}
            function_map[0] = main_categories
            function_map[1] = get_movies_and_music_videos
            function_map[2] = play_video
            function_map[3] = show_recent_sections
            function_map[4] = show_featured_movies
            function_map[5] = show_top_rated_options
            function_map[6] = show_search_box
            function_map[7] = inner_categories
            function_map[8] = show_A_Z
            function_map[9] = show_list
            function_map[10] = show_list
            function_map[11] = show_list
            function_map[12] = display_setting
            function_map[13] = display_BluRay_listings
            function_map[14] = list_music_videos
            function_map[15] = list_movies_from_JSON_API
            function_map[16] = mp3_menu
            print 'submode value 2: ', submode
            function_map[submode](name, url, language, submode)
        except:
            try:
                dialog = xbmcgui.Dialog()
                dialog.ok("Loading at first time", "Downloading necessary files. Won't be shown next time.")
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), '__init__.py')
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'einthusan.py')
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'DBInterface.py')
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'HTTPInterface.py')
                update.downloadPythonFile(os.path.abspath(programPath + "/" + 'resources'), 'JSONInterface.py')
                xbmc.executebuiltin("XBMC.Notification(TamilKodi Notification,Einthusan Movies Loaded,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")
            except:
                xbmc.executebuiltin("XBMC.Notification(TamilKodi Error,Einthusan Import failed,5000,"+xbmcaddon.Addon().getAddonInfo('icon')+")")


    elif mode == 'movie':
       Movie_Main(url)

    elif mode == 'rajmovie':
       Raj_Movie_Main(url)

    elif mode == 'rajshows':
       Raj_Shows(url)

    elif mode == 'gunmovie':
       Gun_Movie_Main(url)

    elif mode == 'tree':
       Main_Tree( url )

    elif mode == 'leaf':
       Main_Leaf( url )
    elif mode == 'leaf_bw':
       Main_Leaf_bw( url )
    elif mode == 'load_videos':
       Load_Video( url )

    elif mode == 'load_gunvideos':
       iconImg = addon.queries.get('iconImg', None)
       Load_GunVideo(url, iconImg)

    elif mode == 'tv':
       tvLink(LIVE_TV1)

    elif mode == 'sportstv':
       tvLink(__SPORTS__)

    elif mode == 'linksakash':
       tvLink(__AKASH__)

    elif mode == 'tv_tree':
       TV_Tree( url )

    elif mode == 'tv_leaf':
       TV_Leaf( url )

    elif mode == 'giniko':
       GinikoURL(url, title, iconImg)

    elif mode == 'yupp':
       YuppURL(url, title, iconImg)

    elif mode == 'tvguide':
       tvGuide(name)

    elif mode == 'settings':
       settings(url)
