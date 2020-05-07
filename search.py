from bs4 import BeautifulSoup
import requests
from . import utils

def smartSearch(url):
    result = {
        "full_name": "",
        "id": "",
        "picture_url": ""
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
        if "/user/" in result["id"]:
            result["username"] = result["id"].partition("/user/")[2].partition("/")[0]
            result["id"] = ""
        else:
            result["id"] = result["id"].split("/")[-1]
            result["username"] = ""
        return result

def searchChannel(query):
    searchUrl = "https://www.youtube.com/results?"
    channelExt =  "EgIQAg%253D%253D"
    searchUrl = utils.includeKeyInUrl(searchUrl, search_query = "+".join(query.lower().split()), sp = channelExt)
    soup = BeautifulSoup(requests.get(searchUrl).text, "html.parser")
    results = []
    for a in soup.find_all('div', {'class': 'yt-lockup-channel'}):
        result = {
            "full_name":"",
            "username": "",
            "url": "",
            "id": "",
            "picture_url": ""
        }
        img = a.find('div', {'class': 'yt-lockup-thumbnail'})
        if img:
            img = img.find('img')
            if img:
                result["picture_url"] = img.get('src', '')
                if result["picture_url"].endswith(".gif"):
                    result["picture_url"] = img.get('data-thumb', '')
                if not result["picture_url"].startswith("http"):
                    result["picture_url"] = "https:" + result["picture_url"]
        img = a.find('div', {'class': 'yt-lockup-content'})
        if img:
            img = img.find('a')
            if img:
                result["full_name"] = img.get('title', '')
                result["url"] = utils.completeYoutubeLink(img.get('href', ''))
                if "/user/" in result["url"]:
                    result["username"] = result["url"].partition("/user/")[2].partition("/")[0]
                    result["id"] = ""
                else:
                    result["id"] = result["url"].split("/")[-1]
                    result["username"] = ""
        results.append(result)
    return {
        "site": "youtube",
        "data": results
    }
