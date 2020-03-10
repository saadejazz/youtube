from bs4 import BeautifulSoup
import requests
import utils

def smartSearch(url):
    result = {
        "name": "",
        "id": "",
        "media_directory": ""
    }
    r = requests.get(url)
    if r.status_code == 404:
        print("No such profile exists")
        return result
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        properties = ["og:title", "og:url", "og:image"]
        keys = list(result.keys())
        for i in range(3):
            k = soup.find('meta', {'property': properties[i]})
            if k:
                result[keys[i]] = k.get('content', '')
        result["id"] = result["id"].split("/")[-1]
        return result

def searchChannel(query):
    searchUrl = "https://www.youtube.com/results?"
    channelExt =  "EgIQAg%253D%253D"
    searchUrl = utils.includeKeyInUrl(searchUrl, search_query = "+".join(query.lower().split()), sp = channelExt)
    soup = BeautifulSoup(requests.get(searchUrl).text, "html.parser")
    results = []
    for a in soup.find_all('div', {'class': 'yt-lockup-channel'}):
        result = {
            "name": "",
            "url": "",
            "id": "",
            "media_directory": ""
        }
        img = a.find('div', {'class': 'yt-lockup-thumbnail'})
#         print(img)
        if img:
            img = img.find('img')
            if img:
                result["media_directory"] = img.get('src', '')
                if result["media_directory"].endswith(".gif"):
                    result["media_directory"] = img.get('data-thumb', '')
                if not result["media_directory"].startswith("http"):
                    result["media_directory"] = "https:" + result["media_directory"]
        img = a.find('div', {'class': 'yt-lockup-content'})
        if img:
            img = img.find('a')
            if img:
                result["name"] = img.get('title', '')
                result["url"] = utils.completeYoutubeLink(img.get('href', ''))
                result["id"] = result["url"].split("/")[-1]
        results.append(result)
    return results
