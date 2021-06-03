# Facebook Friends Scraper
This script can scrape the list of your Facebook friends in 1st degree connections and 2nd degree connections.
It will save a CSV file of your friends.
Also it will check for your disconnected friends (the users that unfriended you).

# Installation
You'll need to have:
1. [Python 3](https://www.python.org/downloads/)
2. pip
3. [Google Chrome](https://www.google.com/chrome/)
4. [Chrome Driver](https://chromedriver.chromium.org/downloads)

Once that's all set up:

1. Clone this repository ```git clone https://github.com/m-primo/facebook-friends```.
2. Go to the cloned directory ```cd facebook-friends```.
3. Install the requirements ```pip install -r requirements.txt```.

# Configuration
Rename `config-example.txt` to `config.txt`.
Then fill your email and password of your Facebook account.
```ini
[credentials]
email=your_email@email.com
password=yourpassword
```

# Run

## 1st degree friend connections (your friends)
1. Run ```python app.py```.
2. It will open a browser window and will fill your username & password automatically.
3. You should see your Facebook friends page and the page will be scrolling to the bottom automatically.
4. A CSV file will be created with the data in the `data` directory with the name `1st-degree_YYYY-MM-DD_HHMM.csv`.

## 2nd degree friend connections (your friend's friends)
*Note: This could take days if you have a lot of friends!*
1. You should have the 1st-degree CSV file. So, get your 1st degree connections first.
2. Put the 1st-degree CSV in the `data` directory.
3. Run ```python app.py data/1st-degree_YYYY-MM-DD_HHMM.csv``` with the actual CSV filename.
4. A browser window will open.
5. You should see the script looping through your Facebook friend's friend pages.
6. A CSV file will be created with the data in the `data` directory with the name `2nd-degree_YYYY-MM-DD_HHMM.csv`.

## Disconnections (who unfriended you)
1. Run ```python app.py data/1st-degree_YYYY-MM-DD_HHMM.csv un```, with the actual CSV filename.
2. It will do the same as "1st degree connections" to get your current friends.
3. You should see who unfriended you, and also it will be saved in CSV file in the `data` directory with the name `1st-degree-disconnections_YYYY-MM-DD_HHMM.csv`.
