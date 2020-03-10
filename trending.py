from bs4 import BeautifulSoup
import utils

def getTrends(driver):
    driver.get("https://www.youtube.com/feed/trending")
    utils.scroll(driver, numScrolls = 20)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    vids = []
    for k in soup.find_all('div', id = 'grid-container'):
        vids += k.find_all('ytd-video-renderer')
    videos = utils.getVideoFromSearch(vids)    
    return videos
    