from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
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
    