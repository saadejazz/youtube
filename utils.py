from selenium.common.exceptions import TimeoutException, JavascriptException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

def setDriver(executable_path, headless = False, maximize = True):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    if maximize:
        chrome_options.add_argument("--start-maximized")
    if headless:
        chrome_options.add_argument("--headless")
    return webdriver.Chrome(executable_path = executable_path, chrome_options=chrome_options)

def completeYoutubeLink(link):
    if link != "":
        if not link.startswith("http"):
            if not link.startswith("/"):
                link = "/" + link
            link = "https://www.youtube.com" + link
    return link

def beautifyText(text):
    return " ".join([a for a in text.replace("\n", "").split() if not a == ""])

def includeKeyInUrl(url, **kwargs):
    for (key, value) in kwargs.items():
        if "?" in url:
            url += '&'
        else:
            url += '?'
        url += f'{key}={value}'
    return url

def scroll(driver, numScrolls = 30):
    for i in range(numScrolls):
        driver.find_element_by_tag_name('body').send_keys(Keys.END)

def getDataFromThumbnails(content):
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
            video["link"] = completeYoutubeLink(a.get('href', ""))
            a = a.find('img')
            if a:
                video['thumbnail_directory'] = a.get('src', "")
        ti = item.find('span', {'class': 'style-scope ytd-thumbnail-overlay-time-status-renderer'})
        if ti:
            video["video_length"] = beautifyText(ti.text)
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

def getDataFromUrl(driver, wait, newUrl):
    # confirm page load
    if driver.current_url != newUrl:
        driver.get(newUrl)
        try:
            wait.until(EC.presence_of_all_elements_located((By.ID, 'dismissable')))
            wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[contains(@class, "ytd-thumbnail-overlay-time-status-renderer")]')))
            scroll(driver)
        except TimeoutException:
            return []

    # extract data
    vids = getDataFromThumbnails(driver.page_source)
    vids = [v for v in vids if v["thumbnail_directory"] != ""]
    return vids

def getVideoFromSearch(vids):
    videos = []
    for vi in vids:
        video = {
            "video_name": "",
            "video_link": "",
            "channel_name": "",
            "channel_link": "",
            "thumbnail_directory": "",
            "video_duration": "",
            "partial_description": "",
            "views": "",
            "timestamp": ""
        }
        i = vi.find('a', id = 'thumbnail')
        if i:
            video["video_link"] = completeYoutubeLink(i.get('href', ''))
            i = i.find('img')
            if i:
                video["thumbnail_directory"] = i.get('src', '')
        i = vi.find('a', id = 'video-title')
        if i:
            video["video_name"] = i.get('title', '')
            aria = i.get('aria-label')
            if aria:
                aria = aria.split()
                if aria[-1] == 'views':
                    video["views"] = aria[-2]
        i = vi.find('div', id = 'byline-container')
        if i:
            i = i.find('ytd-channel-name', id = 'channel-name')
            if i:
                i = i.find('a')
                if i:
                    video["channel_name"] = i.text
                    video["channel_link"] = completeYoutubeLink(i.get('href', ''))
        i = vi.find('div', id = 'metadata-line')
        if i:
            span = i.find_all('span')
            if len(span) >= 2:
                video["timestamp"] = beautifyText(span[1].text)
        i = vi.find('ytd-thumbnail-overlay-time-status-renderer')
        if i:
            i = i.find('span')
            if i:
                video["video_duration"] = beautifyText(i.text)
        i = vi.find('yt-formatted-string', id = 'description-text')
        if i:
            video["partial_description"] = i.text
        videos.append(video)
    return videos
