from yspy.search import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, ChannelSearch
from yspy.extras import Video, Playlist, Suggestions, Hashtag, Comments, Transcript, Channel
from yspy.streamurlfetcher import StreamURLFetcher
from yspy.core.constants import *
from yspy.core.utils import *


__title__        = 'yspy'
__version__      = '1.6.2'
__author__       = 'alexmercerind'
__license__      = 'MIT'


''' Deprecated. Present for legacy support. '''
from yspy.legacy import SearchVideos, SearchPlaylists
from yspy.legacy import SearchVideos as searchYoutube
