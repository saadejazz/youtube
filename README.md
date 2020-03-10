## Crawler for Youtube  
Allows gathering data from [YouTube](https://youtube.com). Two major type of data is gathered:  
* Channels Data  
* Trending Videos 
* Searches 

### Channels:  
For channels, a URL is required:  
```python
from utils import setDriver
from channels import Channel

# set driver and url
driver = setDriver(executable_path = 'path/to/chromedriver', headless = False, maximize = True)
url = "https://www.youtube.com/channel/UCky4jqybV5XHnLg0egiBCkg"

# start scraping
data = Channel(url = url).getCompleteProfile()

# print the results. Results are in the form of a dictionary
print(data)
```
**Important Info:**  
* Initiating a driver instance requires a chromedriver executable which can be downloaded from [here](https://chromedriver.chromium.org/downloads). Give the path of the driver to the **executable_path** argument of the **setDriver** function. Make sure you have chrome installed, and have execution permissions for the driver. The driver version should be the same as your installed chrome application.    
* **getCompleteProfile()** takes two optional arguments: **include** and **exclude** to conduct a partial crawl comprising of some attributes. The list of allowed attributes is:  
  * *overview*
  * *videos*
  * *posts*
  * *channels*
  * *playlists*  

One can provide attributes to be *either* included or excluded from the crawl, not both (If both arguments are provided, include will take precedence). An example is shown below
```python
include = ["overview", "posts", "playlists"]
data = Channel(url = url).getCompleteProfile(include = include)
```
  
### Trending:
To get youtube trends, use:  
```python
from utils import setDriver
from trending import getTrends

driver = setDriver(executable_path = 'path/to/chromedriver', headless = False, maximize = True)
data = getTrends(driver)

# print the result. The result is a list of trending videos
print(data)
```
  
### Searches:   
Results from two types of searches can be collected:  
* Smart Search -- Gets the following data given a channel url:
  * Name
  * Unique identifier
  * Profile picture link
* Channel Search -- Gets a list of channels given some keywords/query as arguments

#### Smart Search:  
```python
from search import smartSearch

url = "https://www.youtube.com/channel/UCky4jqybV5XHnLg0egiBCkg"
data = smartSearch(url)
print(data)
```

#### Channel Search:  
```python
from search import searchChannel

query = "The Voice"
data = searchChannel(query)
print(data)
```
