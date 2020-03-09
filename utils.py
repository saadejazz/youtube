from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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
    if not link.startswith("http"):
        if not link.startswith("/"):
            link = "/" + link
        link = "https://www.facebook.com" + link
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

def scroll(driver, numScrolls = 20000, fastScroll = False):
    scroll_time = 5
    if fastScroll:
        driver.execute_script("document.body.style.transform = 'scale(0.05)'")
    current_scrolls = 0
    old_height = 0
    sleep(0.5)
    while True:
        try:
            if current_scrolls == numScrolls:
                return
            try:
                old_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(driver, scroll_time, 0.05).until(
                    lambda driver: check_height(driver, old_height)
                )
                current_scrolls += 1
            except JavascriptException:
                pass
        except TimeoutException:
            break
    driver.execute_script("document.body.style.transform = 'scale(1.00)'")
    return

def check_height(driver, old_height):
    new_height = driver.execute_script("return document.body.scrollHeight")
    return new_height != old_height