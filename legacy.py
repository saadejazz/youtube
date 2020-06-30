# def searchChannel(query):
#     searchUrl = "https://www.youtube.com/results?"
#     channelExt =  "EgIQAg%253D%253D"
#     searchUrl = utils.includeKeyInUrl(searchUrl, search_query = "+".join(query.lower().split()), sp = channelExt)
#     soup = BeautifulSoup(requests.get(searchUrl).text, "html.parser")
#     results = []
#     print(soup)
#     for a in soup.find_all('div', {'class': 'yt-lockup-channel'}):
#         result = {
#             "full_name":"",
#             "username": "",
#             "url": "",
#             "id": "",
#             "picture_url": ""
#         }
#         img = a.find('div', {'class': 'yt-lockup-thumbnail'})
#         if img:
#             img = img.find('img')
#             if img:
#                 result["picture_url"] = img.get('src', '')
#                 if result["picture_url"].endswith(".gif"):
#                     result["picture_url"] = img.get('data-thumb', '')
#                 if not result["picture_url"].startswith("http"):
#                     result["picture_url"] = "https:" + result["picture_url"]
#         img = a.find('div', {'class': 'yt-lockup-content'})
#         if img:
#             img = img.find('a')
#             if img:
#                 result["full_name"] = img.get('title', '')
#                 result["url"] = utils.completeYoutubeLink(img.get('href', ''))
#                 if "/user/" in result["url"]:
#                     result["username"] = result["url"].partition("/user/")[2].partition("/")[0]
#                     result["id"] = ""
#                 else:
#                     result["id"] = result["url"].split("/")[-1]
#                     result["username"] = ""
#         results.append(result)
#     return {
#         "site": "youtube",
#         "data": results
#     }