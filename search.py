from bs4 import BeautifulSoup
import requests
from . import utils
import json


HEADERS = {
        "Host": "www.youtube.com",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def smartSearch(url):
    result = {
        "full_name": "",
        "id": "",
        "picture_url": "",
        "username": ""
    }
    r = requests.get(url, headers = HEADERS)
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
    for _ in range(3):
        soup = BeautifulSoup(requests.get(searchUrl, headers = HEADERS).text, "html.parser")
        script = soup.find(lambda tag: tag.name == 'script' and 'window["ytInitialData"]' in tag.text)
        if script:
            break
    results = []
    if script:
        jso = str(script).partition('window["ytInitialData"] = ')[2].partition("};")[0]
        jso += "}"
        try:
            j = json.loads(jso)
        except json.JSONDecodeError:
            return []
        try:
            j = j["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        except (KeyError, IndexError):
            return []
        for vid in j:
            result = {
                "full_name":"",
                "username": "",
                "url": "",
                "id": "",
                "picture_url": ""
            }
            try:
                vid = vid["channelRenderer"]
                result["picture_url"] = vid["thumbnail"]["thumbnails"][-1]["url"]
                if result["picture_url"].startswith("//"):
                    result["picture_url"] = "https:" + result["picture_url"]
                result["id"] = vid["channelId"]
                result["full_name"] = vid["title"]["simpleText"]
                result["url"] = vid["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                if result["url"].startswith("/"):
                    result["url"] = "https://www.youtube.com" + result["url"]
                if "/user/" in result["url"]:
                    result["username"] = result["url"].partition("/user/")[2].partition("/")[0]
                results.append(result)
            except (KeyError, IndexError):
                pass
    return {
        "site": "youtube",
        "data": results
    }

def searchVideos(query):
    query = "+".join(query.split())
    # this loop confirms that the page with the required script tag is loaded. Sometimes alternate page is received.
    for _ in range(3):
        r = requests.get("https://www.youtube.com/results?search_query={}&sp=EgIQAQ%253D%253D".format(query), headers = HEADERS)
        soup = BeautifulSoup(r.text, "html.parser").find("body")
        script = soup.find(lambda tag: tag.name == 'script' and 'window["ytInitialData"]' in tag.text)
        if script:
            break
    results = []
    if script:
        jso = str(script).partition('window["ytInitialData"] = ')[2].partition("};")[0]
        jso += "}"
        try:
            j = json.loads(jso)
        except json.JSONDecodeError:
            return []
        try:
            j = j["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        except (KeyError, IndexError):
            return []
        for vid in j:
            result = {
                "title": "",
                "url": "",
                "thumbnail_url": ""
            }
            try:
                vid = vid["videoRenderer"]
                result["thumbnail_url"] = vid["thumbnail"]["thumbnails"][0]["url"]
                result["title"] = vid["title"]["runs"][0]["text"]
                result["url"] = vid["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
                if result["url"].startswith("/"):
                    result["url"] = "https://www.youtube.com" + result["url"]
                results.append(result)
            except (KeyError, IndexError):
                pass
    return {
        "site": "youtube",
        "data": results
    }
