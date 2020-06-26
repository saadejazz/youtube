from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import unquote
from bs4 import BeautifulSoup
from time import sleep
import utils
import re

class Channel():
    def __init__(self, driver, url):
        self.url = url
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        self.origin = "https://www.facebook.com/"
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 3)
        self.attributes = ["overview", "videos", "playlists", "channels", "posts"]
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
            "channels":{
                "featured": [],
                "subscribed": []
            },
            "playlists": [],
            "posts": []
        }
    
    def initiatePostSkeleton(self):
        return {
                "post_author":{
                    "name": "",
                    "link": "",
                    "media_directory": ""
                },
                "post_link": "",
                "timestamp": "",
                "post_type":{
                    "is_text": False,
                    "is_picture": False,
                    "is_video": False,
                    "is_vote": False
                },
                "post_text": "",
                "picture_links": [],
                "video_links": [],
                "other_links": [],
                "votes": {
                    "vote_text": "",
                    "vote_options": [],
                    "total_votes": 0
                },
                "post_likes": 0,
                "post_comments": []
            }

    def initiateCommentSkeleton(self):
        return {
                "comment_author":{
                    "name": "",
                    "link": "",
                    "media_directory": ""
                },
                "comment_url": "",
                "timestamp": "",
                "comment_text": "",
                "comment_links": [],
                "comment_likes": 0
                }

    def overview(self):
        # navigating to page
        if self.driver.current_url != self.url + "/about":
            self.driver.get(self.url + "/about")
            sleep(0.4)
        
        overview = {
            "name": "",
            "url": "",
            "media_directory": "",
            "subscriber_count": "",
            "is_verified": False,
            "description": "",
            "location": "",
            "web_links": [],
            "joining_date": "",
            "total_views":""
        }

        # extracting name, url, image from meta tags
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        n = soup.find('meta', {'property': 'og:url'})
        if n:
            overview["url"] = n.get('content', '')
        n = soup.find('meta', {'property': 'og:title'})
        if n:
            overview["name"] = n.get('content', '')
        n = soup.find('meta', {'property': 'og:image'})
        if n:
            overview["media_directory"] = n.get('content', '')

        # extracting verification status and subscriber count
        n = soup.find('div', id = 'channel-container')
        if n:
            nam = n.find('ytd-badge-supported-renderer', {'class': 'ytd-channel-name'})
            if nam:
                nam = nam.find('svg')
                if nam:
                    overview["is_verified"] = True
            nam = n.find('yt-formatted-string', id = 'subscriber-count')
            if nam:
                text = nam.text
                if text != "":
                    overview["subscriber_count"] = text.split()[0]

        # extracting description
        n = soup.find('yt-formatted-string', id = 'description')
        if n:
            overview["description"] = n.text

        # extracting location    
        n = soup.find('div', id = 'details-container')
        if n:
            n = n.find(lambda tag: tag.name == 'td' and "Location:" in tag.text)
            if n:
                n = n.findNext('td')
                if n:
                    overview["location"] = n.text.replace('\n', '')

        # extracting web links            
        n = soup.find('div', id = 'link-list-container')
        if n:
            for a in n.find_all('a'):
                link = {}
                link["link_type"] = a.text.replace('\n', '')
                link["redirect_url"] = unquote(a.get('href', '')).partition('q=')[2].partition("&")[0]
                overview["web_links"].append(link)

        # extracting joining date and views        
        n = soup.find('div', id = 'right-column')
        if n:
            nam = n.find(lambda tag: tag.name == 'yt-formatted-string' and "Joined" in tag.text)
            if nam:
                text = nam.text
                if text != "" and len(text.split()) >= 2:
                    overview["joining_date"] = " ".join(text.split()[1:])
            nam = n.find(lambda tag: tag.name == 'yt-formatted-string' and "views" in tag.text)
            if nam:
                text = nam.text
                if text != "":
                    overview["total_views"] = text.split()[0]
        
        self.profile["overview"] = overview
        return overview

    def getVideos(self):
        # for popular uploads
        newUrl = utils.includeKeyInUrl(self.url + "/videos", view = "0", sort = "p", flow = "grid")
        self.profile["videos"]["popular"] = utils.getDataFromUrl(self.driver, self.wait, newUrl)
        
        # for newest uploads
        newUrl = utils.includeKeyInUrl(self.url + "/videos", view = "0", sort = "dd", flow = "grid")
        self.profile["videos"]["new"] = utils.getDataFromUrl(self.driver, self.wait, newUrl)

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

    def getPosts(self):
        # navigating to page
        newUrl = self.url + "/community"
        if self.driver.current_url != newUrl:
            self.driver.get(newUrl)
            utils.scroll(self.driver)
            sleep(1)
        
        content = str(self.driver.page_source)
        
        # open comments
        comm = re.findall(r'View all [0-9]+ comments', content)
        comm += re.findall(r'View comment', content)
        for co in comm:
            elements = self.driver.find_elements_by_xpath("//*[text()[contains(.,'" + co + "')]]")
            for element in elements:
                self.driver.execute_script("arguments[0].click();", element)
        try:
            self.wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'ytd-comment-thread-renderer')))
        except TimeoutException:
            pass

        sleep(1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        blocks = soup.find_all('ytd-backstage-post-thread-renderer')
        posts = []

        # extracting post one by one
        for block in blocks:
            post = self.initiatePostSkeleton()

            # extracting author link and picture
            a = block.find('div', id = 'author-thumbnail')
            if a:
                a = a.find('a')
                if a:
                    post["post_author"]["link"] = utils.completeYoutubeLink(a.get('href', ''))
                    img = a.find('img')
                    if img:
                        post["post_author"]["media_directory"] = img.get('src', "")
            
            # extracting author name
            a = block.find('a', id = 'author-text')
            if a:
                post["post_author"]["name"] = utils.beautifyText(a.text)
            
            # extracting post link and pubish time
            a = block.find('yt-formatted-string', id = 'published-time-text')
            if a:
                a = a.find('a')
                if a:
                    post["timestamp"] = a.text
                    post["post_link"] = utils.completeYoutubeLink(a.get('href', ''))
            
            # extracting text
            a = block.find('yt-formatted-string', id = 'content-text')
            if a:
                post["post_type"]["is_text"] = True
                post["post_text"] = a.text.replace('\ufeff', '')
                
            # extracting vote data
            v = block.find('ytd-backstage-poll-renderer', id = 'poll-attachment')
            if v:
                a = v.find('yt-formatted-string', id = 'vote-info')
                if a:
                    count = a.text.split()[0]
                    if count.isnumeric():
                        post["votes"]["total_votes"] = int(count)
                        post["post_type"]["is_vote"] = True
                        post["votes"]["vote_text"] = post["post_text"]
                        a = v.find_all('yt-formatted-string', {'class': 'choice-text'})
                        for choice in a:
                            post["votes"]["vote_options"].append(choice.text)
                    
            # getting likes
            a = block.find('span', id = 'vote-count-middle')
            if a:
                count = utils.beautifyText(a.text)
                if count.isnumeric():
                    post["post_likes"] = int(count)
                    
            # getting links
            a = []
            srcs = []
            b = block.find('div', id = 'content')
            c = block.find('div', id = 'content-attachment')
            for y in [b, c]:
                if y:
                    a += y.find_all('a')
                    srcs += y.find_all('img')
            for link in a:
                link = utils.completeYoutubeLink(link.get('href', ""))
                if "/watch?" in link:
                    post["post_type"]["is_video"] = True
                    post["video_links"].append(link)
                elif link not in [post["post_link"], self.url, '', self.origin]:
                    post["other_links"].append(link)
            for img in srcs:
                post["post_type"]["is_picture"] = True
                src = img.get('src', '')
                if src != '':
                    post["picture_links"].append(src)
            
            # removing duplicate links
            for option in ["picture_links", "video_links", "other_links"]:
                post[option] = list(set(post[option]))

            # getting comments
            for com in block.find_all('ytd-comment-thread-renderer'):
                comment = self.initiateCommentSkeleton()
                a = com.find('div', id = 'author-thumbnail')
                if a:
                    a = a.find('a')
                    if a:
                        comment["comment_author"]["link"] = utils.completeYoutubeLink(a.get('href', ''))
                        img = a.find('img')
                        if img:
                            comment["comment_author"]["media_directory"] = img.get('src', "")
                a = com.find('a', id = 'author-text')
                if a:
                    comment["comment_author"]["name"] = utils.beautifyText(a.text)
                a = com.find('yt-formatted-string', {'class': 'published-time-text'})
                if a:
                    a = a.find('a')
                    if a:
                        comment["timestamp"] = a.text
                        comment["comment_url"] = utils.completeYoutubeLink(a.get('href', ''))
                a = com.find('yt-formatted-string', id = 'content-text')
                if a:
                    comment["comment_text"] = a.text.replace('\ufeff', '')
                    for link in a.find_all('a'):
                        comment["comment_links"].append(utils.completeYoutubeLink(link.get('href', '')))
                a = com.find('span', id = 'vote-count-middle')
                if a:
                    count = utils.beautifyText(a.text)
                    if count.isnumeric():
                        comment["comment_likes"] = int(count)
                post["post_comments"].append(comment)
            posts.append(post)
        self.profile["posts"] = posts
        return posts

    def getAssociatedChannels(self):
        # navigate to page
        newUrl = self.url + "/channels"
        if self.driver.current_url != newUrl:
            self.driver.get(newUrl)
            sleep(1)

        # extraction
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        primary = soup.find('ytd-section-list-renderer', {'page-subtype': 'channels'})
        if primary:
            options = primary.find_all('div', id ='dismissable')
            for option in options:
                ch = []
                for chan in option.find_all('div', id = 'channel'):
                    channel = {
                        "name": '',
                        "link": '',
                        "media_directory": '',
                        'subscribers': ""
                    }
                    info = chan.find('a', id = 'channel-info')
                    if info:
                        channel["link"] = utils.completeYoutubeLink(info.get('href', ''))
                        img = chan.find('img')
                        if img:
                            channel["media_directory"] = img.get('src', '')
                        img = chan.find('span', id = 'title')
                        if img:
                            channel["name"] = utils.beautifyText(img.text)
                        img = chan.find('span', id = 'thumbnail-attribution')
                        if img.text != '':
                            channel["subscribers"] = img.text.split()[0]
                        ch.append(channel)
                pri = option.find('div', id = 'title-container')
                if pri:
                    pri = pri.find('span', id = 'title')
                    if pri.text == "Featured Channels":
                        self.profile["channels"]["featured"] = ch
                    elif pri.text == "Subscriptions":
                        self.profile["channels"]["subscribed"] = ch
        return self.profile["channels"]

    def getCompleteProfile(self, include = None, exclude = None):
        self.driver.get(self.url + "/videos")
        a = self.driver.current_url
        if "error?" in a and "404" in a:
            print("profile does not exist")
            return None
        else:
            if include:
                final = [attr for attr in include if attr in self.attributes]
            elif exclude:
                final = [attr for attr in self.attributes if attr not in exclude]
            else:
                final = self.attributes

            if "overview" in final:
                self.overview()
            if "videos" in final:
                self.getVideos()
            if "posts" in final:
                self.getPosts()
            if "channels" in final:
                self.getAssociatedChannels()
            if "playlists" in final:
                self.getPlaylists()
            
            return self.profile
