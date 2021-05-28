# Facebook Friends Scraper
This script can scrape a list of your Facebook friends in 1st degree connections and 2nd degree connections. 
It will save a CSV file of your friends.
Also it will check for your disconnected friends (the users that unfriended you).

## Installation
You'll need to have:
1. python 3
2. pip
3. [Google Chrome](https://www.google.com/chrome/)
4. [Selenium Webdriver](http://selenium-python.readthedocs.io/installation.html)

Once that's all set up:

1. Clone this repository.
2. Go to the cloned directory ```cd facebook-friends```.
3. Install the requirements ```pip install -r requirements.txt```.

## Configuration
Copy `config-example.txt` file and rename it to `config.txt`.
Then fill your email and password of your Facebook account.
```
[credentials]
email=your_email@email.com
password=yourpassword
```

## Run

### 1st degree friend connections (your friends)
1. Run ```python facebook-friends.py```.
2. It will open a browser window and will fill your username & password automatically.
3. You should see your Facebook friends page and the page will be scrolling to the bottom automatically.
4. A CSV file will be created with the data (1st-degree_YYYY-MM-DD_HHMM.csv).

### 2nd degree friend connections (your friend's friends)
<i>Note: This could take days if you have lots of friends!</i>
1. Get your 1st degree connections first, so you should have the 1st-degree CSV file.
2. Put the 1st-degree CSV in the same directory as `facebook-friends.py`.
3. Run ```python facebook-friends.py 1st-degree_YYYY-MM-DD_HHMM.csv```, with the actual CSV filename.
4. A browser window will open.
5. You should see the script looping through your Facebook friend's friend pages.
6. A CSV file will be created with the data (2nd-degree_YYYY-MM-DD_HHMM.csv).
