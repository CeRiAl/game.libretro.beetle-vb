'''
    3D Enabler [for] Samsung TV - addon for XBMC to enable 3D mode
    Copyright (C) 2014  Pavel Kuzub

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import simplejson
import socket
import re
import urllib2
from xml.dom.minidom import parseString
import base64
import uuid
import select
from pprint import pprint

__addon__   = xbmcaddon.Addon()
libs = os.path.join(__addon__.getAddonInfo('path'), 'lib')
sys.path.append(libs)

class Settings(object):
    def __init__(self):
        self.addonname      = __addon__.getAddonInfo('name')
        self.icon           = __addon__.getAddonInfo('icon')
        self.isPlaying      = False
        self.currentFile    = ''

class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        
    def isPlayingVBGame(self):
        filePath = xbmc.Player().getPlayingFile()
        fileExtension = os.path.splitext(filePath)[1]
        if fileExtension in ('.vb', '.vboy'):
            return True 
        return False
    
    def onNotification(self, sender, method, data):
        xbmc.log('YYYY Notification Received: ' + str(sender) + ': ' + str(method) + ': ' + str(data), xbmc.LOGDEBUG)
        stereo_mode = str(__addon__.getSetting('vb_3d_mode'))
        gui_stereo = getStereoscopicMode()
        gui_stereo_mode = xbmc.getInfoLabel('System.StereoscopicMode')
        xbmc.log('YYYY System.StereoscopicMode: ' + str(gui_stereo_mode), xbmc.LOGDEBUG)
        
        if stereo_mode == 'sidebyside':
            if method == 'Player.OnPlay':
                if self.isPlayingVBGame():
                    settings.isPlaying = True
                    settings.currentFile = xbmc.Player().getPlayingFile()
                    xbmc.log('YYYY Should activate SBS', xbmc.LOGDEBUG)
                    xbmc.executebuiltin('XBMC.SetStereoMode("split_vertical")')
            elif method == 'Player.OnStop':
                if settings.isPlaying:
                    settings.isPlaying = False
                    settings.currentFile = ''
                    xbmc.log('YYYY Should stop SBS', xbmc.LOGDEBUG)
                    xbmc.executebuiltin('XBMC.SetStereoMode("off")')

def getStereoscopicMode():
    query = '{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["stereoscopicmode"]}, "id": 1}'
    result = xbmc.executeJSONRPC(query)
    json = simplejson.loads(result)
    xbmc.log('YYYY Received JSON response: ' + str(json), xbmc.LOGDEBUG)
    ret = 'unknown'
    if json.has_key('result'):
        if json['result'].has_key('stereoscopicmode'):
            if json['result']['stereoscopicmode'].has_key('mode'):
                ret = json['result']['stereoscopicmode']['mode'].encode('utf-8')
    # "off", "split_vertical", "split_horizontal", "row_interleaved"
    # "hardware_based", "anaglyph_cyan_red", "anaglyph_green_magenta", "monoscopic"
    return ret

def main():
    global dialog, dialogprogress, blackScreen, responseMap, settings, monitor
    dialog = xbmcgui.Dialog()
    dialogprogress = xbmcgui.DialogProgress()
    blackScreen = xbmcgui.Window(-1)
    settings = Settings()
    monitor = MyMonitor()
    
    gui_stereo = getStereoscopicMode()
    
    while not xbmc.abortRequested:
        xbmc.sleep(1000)
    onAbort()

if __name__ == '__main__':
    main()
