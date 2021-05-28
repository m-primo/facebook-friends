# --------------- Import -----------------
import os, datetime, time, csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import configparser
from sys import argv
import random
# ---------------  -----------------
print("\n" * 10)
os.environ["DEBUSSY"] = "1"
# --------------- Configure browser session -----------------
wd_options = Options()
wd_options.add_argument("--disable-notifications")
wd_options.add_argument("--disable-infobars")
wd_options.add_argument("--mute-audio")
browser = webdriver.Chrome(chrome_options=wd_options)
# --------------- Ask user to log in -----------------
def fb_login(credentials):
    print("Opening browser...")
    email = credentials.get('credentials', 'email')
    password = credentials.get('credentials', 'password')
    browser.get("https://facebook.com/")
    browser.find_element_by_name('email').send_keys(email)
    browser.find_element_by_name('pass').send_keys(password)
    browser.find_element_by_name('login').click()
# --------------- Scroll to bottom of page -----------------
def scroll_to_bottom():
    SCROLL_PAUSE_TIME = 1
    count = 1
    # Get scroll height
    # last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        if count == 5:
            break
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        count += 1
        # # Calculate new scroll height and compare with last scroll height
        # new_height = browser.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        #   break
        # last_height = new_height
# --------------- Get list of all friends on page ---------------
def scan_friends():
    print('Scanning page for friends...')
    friends = []
    # friend_cards = browser.find_elements_by_xpath("//div[@data-sigil='undoable-action']/a")
    friend_cards = browser.find_elements_by_css_selector("div#root div.timeline div[data-sigil='undoable-action'] a")
    for friend in friend_cards:
        # if friend.get_attribute('data-hovercard') is None:
        #   print(" %s (INACTIVE)" % friend.text)
        #   friend_id = friend.get_attribute('ajaxify').split('id=')[1]
        #   friend_active = 0
        # else:
        #   print(" %s" % friend.text)
        #   friend_id = friend.get_attribute('data-hovercard').split('id=')[1].split('&')[0]
        #   friend_active = 1
        friend_name = friend.text
        friend_id = friend.get_attribute('href')
        if friend_name:
            friends.append({
                'name': friend_name.encode('utf-8', 'ignore'), #to prevent CSV writing issues
                'id': friend_id
            })
    print('Found %r friends on page!' % len(friends))
    return friends
# ----------------- Load list from CSV -----------------
def load_csv(filename):
    inact = 0
    myfriends = []
    with open(filename, 'rt', encoding="utf-8") as input_csv:
        reader = csv.DictReader(input_csv)
        for idx,row in enumerate(reader):
            if row['active'] is '1':
                myfriends.append({
                    "name":row['B_name'],
                    "uid":row['B_id']
                })
            else:
                print("Skipping %s (inactive)" % row['B_name'])
                inact = inact + 1
    print("%d friends in imported list" % (idx+1))
    print("%d ready for scanning (%d inactive)" % (idx-inact+1, inact))
    return myfriends
# --------------- Scrape 1st degree friends ---------------
def scrape_1st_degrees():
    #Prep CSV Output File
    csvOut = '1st-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'w', encoding="utf-8"))
    writer.writerow(['id','name'])

    #Get your unique Facebook ID
    # profile_icon = browser.find_element_by_css_selector("[data-click='profile_icon'] > a > span > img")
    # myid = profile_icon.get_attribute("id")[19:]
    # profile_icon = browser.find_element_by_css_selector("[id='profile_tab_jewel'] > a")
    # myid = profile_icon.get_attribute("href")
    # myid = 0
    time.sleep(1)
    browser.get("https://m.facebook.com/home.php")
    time.sleep(1)
    profile_icon = browser.find_element_by_css_selector("[id='profile_tab_jewel'] > a")
    myid = profile_icon.get_attribute("href").split("?")[0]
    time.sleep(1)

    #Scan your Friends page (1st-degree friends)
    print("Opening Friends page...")
    browser.get(myid+"/friends")
    time.sleep(2)
    scroll_to_bottom()
    time.sleep(2)
    myfriends = scan_friends()

    #Write friends to CSV File
    for friend in myfriends:
        writer.writerow([friend['id'],str(friend['name'])])

    print("Successfully saved to %s" % csvOut)
# --------------- Scrape 2nd degree friends. ---------------
#This can take several days if you have a lot of friends!!
def scrape_2nd_degrees():
    #Prep CSV Output File
    csvOut = '2nd-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'w', encoding="utf-8"))
    writer.writerow(['A_id', 'B_id', 'A_name','B_name','active'])

    #Load friends from CSV Input File
    script, filename = argv
    print("Loading list from %s..." % filename)
    myfriends = load_csv(filename)
    print("------------------------------------------")
    for idx,friend in enumerate(myfriends):
        #Load URL of friend's friend page
        scrape_url = "https://www.facebook.com/"+ friend['uid'] + "/friends?source_ref=pb_friends_tl"
        browser.get(scrape_url)

        #Scan your friends' Friends page (2nd-degree friends)
        print("%d) %s" % (idx+1, scrape_url))
        scroll_to_bottom()
        their_friends = scan_friends()

        #Write friends to CSV File
        print('Writing friends to CSV...')
        for person in their_friends:
            writer.writerow([friend['uid'],person['id'],friend['name'],person['name'],person['active']])
# --------------- Start Scraping ---------------
now = datetime.now()
configPath = "config.txt"
if configPath:
    configObj = configparser.ConfigParser()
    configObj.read(configPath)
    email = configObj.get('credentials', 'email')
    password = configObj.get('credentials', 'password')
else:
    print('Enter the config path')
fb_login(configObj)

if len(argv) is 1:
    scrape_1st_degrees()
elif len(argv) is 2:
    scrape_2nd_degrees()
else:
    print("Invalid # of arguments specified. Use none to scrape your 1st degree connections, or specify the name of the CSV file as the first argument.")
