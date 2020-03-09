from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from time import time, sleep
import datetime
import utils
import json

class Channel():
    def __init__(self, driver, url):
        self.url = url
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 3)
        self.attributes = ["overview", "videos", "playlists", "posts"]
        self.initiateNullSkeleton()

    def __str__(self):
        return f'Youtube Channel: "{self.url}"'
    
    def initiateNullSkeleton(self):
        self.profile = {
            "overview": {},
            "videos": {
                "popular": [],
                "new": []
            },
            "playlists": [],
            "posts": []
        }
    
    def getDataFromThumbnails(self, content):
        soup = BeautifulSoup(content, "html.parser")
        contents = soup.find('div', id = 'contents')
        videos = []
        for item in contents.find_all('div', id = 'dismissable'):
            aria = False
            video = {
                "name": "",
                "link": "",
                "video_length": "",
                "thumbnail_directory": "",
                "views": "",
                "timestamp": ""
            }
            a = item.find('a')
            if a:
                video["link"] = utils.completeYoutubeLink(a.get('href', ""))
                a = a.find('img')
                if a:
                    video['thumbnail_directory'] = a.get('src', "")
            ti = item.find('span', {'class': 'style-scope ytd-thumbnail-overlay-time-status-renderer'})
            if ti:
                video["video_length"] = utils.beautifyText(ti.text)
            item = item.find('div', id = 'details')
            if item:
                a = item.find('a', id = 'video-title')
                if a:
                    video["name"] = a.text
                    aria = a.get('aria-label')
                    if aria:
                        video["views"] = aria.split()[-2]
                        aria = True
                item = item.find('div', id = 'metadata-line')
                if item:
                    span = item.find_all('span', {'class': 'style-scope ytd-grid-video-renderer'})
                    if len(span) >= 2:
                        if not aria:    
                            video["views"] = span[0].text
                        video["timestamp"] = span[1].text
            videos.append(video)
        return videos

    def getDataFromUrl(self, newUrl):
        # confirm page load
        if self.driver.current_url != newUrl:
            self.driver.get(newUrl)
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.ID, 'dismissable')))
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "ytd-thumbnail-overlay-time-status-renderer")]')))
            except TimeoutException:
                return []

        # extract data
        vids = self.getDataFromThumbnails(self.driver.page_source)
        vids = [v for v in vids if v["thumbnail_directory"] != ""]
        return vids

    def getVideos(self):
        # for popular uploads
        newUrl = utils.includeKeyInUrl(self.url + "/videos", view = "0", sort = "p", flow = "grid")
        self.profile["videos"]["popular"] = self.getDataFromUrl(newUrl)
        
        # for newest uploads
        newUrl = utils.includeKeyInUrl(self.url + "/videos", view = "0", sort = "dd", flow = "grid")
        self.profile["videos"]["new"] = self.getDataFromUrl(newUrl)

        return self.profile["videos"]
    
    def getPlaylists(self):
        # navigate to page
        newUrl = self.url + "/playlists"
        if self.driver.current_url != newUrl:
            self.driver.get(newUrl)

        plays = self.wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "ytd-grid-playlist-renderer")))
        playlists = []
        for play in plays:
            play = BeautifulSoup(play.get_attribute("innerHTML"), "html.parser")
            playlist = {
                "name": "",
                "link": "",
                "thumbnail_directory": "",
                "num_videos": ""
            }
            a = play.find('a', id = 'thumbnail')
            if a:
                playlist["link"] = utils.completeYoutubeLink(a.get('href', ""))
                a = a.find('img')
                if a:
                    playlist["thumbnail_directory"] = a.get('src', "")
            a = play.find('a', id = 'video-title')
            if a:
                playlist["name"] = a.text
            a = play.find('yt-formatted-string', {'class': 'ytd-thumbnail-overlay-side-panel-renderer'})
            if a:
                playlist["num_videos"] = a.text
            playlists.append(playlist)
        
        self.profile["playlists"] = playlists
        return playlists
    