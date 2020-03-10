from bs4 import BeautifulSoup
import utils

def getTrends(driver):
    driver.get("https://www.youtube.com/feed/trending")
    utils.scroll(driver, numScrolls = 20)
    videos = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    vids = []
    for k in soup.find_all('div', id = 'grid-container'):
        vids += k.find_all('ytd-video-renderer')
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
            video["video_link"] = utils.completeYoutubeLink(i.get('href', ''))
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
                    video["channel_link"] = utils.completeYoutubeLink(i.get('href', ''))
        i = vi.find('div', id = 'metadata-line')
        if i:
            span = i.find_all('span')
            if len(span) >= 2:
                video["timestamp"] = utils.beautifyText(span[1].text)
        i = vi.find('ytd-thumbnail-overlay-time-status-renderer')
        if i:
            i = i.find('span')
            if i:
                video["video_duration"] = utils.beautifyText(i.text)
        i = vi.find('yt-formatted-string', id = 'description-text')
        if i:
            video["partial_description"] = i.text
        videos.append(video)
    return videos
    