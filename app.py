# ---------------> Import <-----------------
import os, datetime, time, csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import configparser
from sys import argv
import random
# ---------------> Env <-----------------
os.environ["DEBUSSY"] = "1"
# ---------------> Configure browser session <-----------------
def create_browser():
    wd_options = Options()
    wd_options.add_argument("--disable-notifications")
    wd_options.add_argument("--disable-infobars")
    wd_options.add_argument("--mute-audio")
    browser = webdriver.Chrome(options=wd_options)
    return browser
# ---------------> Ask user to log in <-----------------
def fb_login(credentials):
    email = credentials.get('credentials', 'email')
    password = credentials.get('credentials', 'password')
    browser.get("https://facebook.com/")
    print("[*] Logging to the fb account...")
    browser.find_element_by_name('email').send_keys(email)
    browser.find_element_by_name('pass').send_keys(password)
    browser.find_element_by_name('login').click()
# ---------------> Scroll to bottom of the page <-----------------
def scroll_to_bottom():
    try:
        while browser.find_element_by_css_selector('#m_more_friends'):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)
    except:
        pass
# ---------------> Get list of all friends on page <---------------
def scan_friends():
    print('[*] Scanning the page for friends...')
    friends = []
    friend_cards = browser.find_elements_by_css_selector("div#root div.timeline div[data-sigil='undoable-action'] a")
    friend_mutual_cards = browser.find_elements_by_css_selector("div#root div.timeline div[data-sigil='undoable-action'] [data-sigil='m-add-friend-source-replaceable']")
    index = 0
    for friend in friend_cards:
        friend_name = friend.text
        friend_id = friend.get_attribute('href')
        if friend_id is not None: friend_id = friend_id.split("/")[-1]
        if friend_name:
            friends.append({
                'name': friend_name, #to prevent CSV writing issues .encode('utf-8', 'ignore')
                'id': friend_id
            })
        index += 1
    index = 0
    for friend in friends:
        mutuals = friend_mutual_cards[index].text.split(" ")[0].strip()
        if not mutuals.isnumeric(): mutuals = ''
        friend.update({'mutuals': mutuals})
        index += 1
    print('[+] Found %r friends on page!' % len(friends))
    return friends
# -----------------> Load list from CSV <-----------------
def load_csv(filename):
    myfriends = []
    with open(filename, 'rt', newline='', encoding="utf-8") as input_csv:
        reader = csv.DictReader(input_csv)
        for idx,row in enumerate(reader):
            myfriends.append({
                "name": row['name'],
                "id": row['id'],
                "mutuals": row['mutuals']
            })
    print("[+] %d friends in imported list" % (idx+1))
    return myfriends
# ---------------> Scrape 1st degree friends <---------------
def scrape_1st_degrees():
    start_time = time.time()

    #Prep CSV Output File
    csvOut = 'data/1st-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'wt', newline='', encoding="utf-8"))
    writer.writerow(['id', 'name', 'mutuals'])

    #Get my Facebook id
    print("[*] Scanning for my ID...")
    time.sleep(1)
    browser.get("https://m.facebook.com/home.php")
    time.sleep(1)
    profile_icon = browser.find_element_by_css_selector("[id='profile_tab_jewel'] > a")
    myid = profile_icon.get_attribute("href").split("?")[0]
    time.sleep(1)

    #Scan your Friends page (1st-degree friends)
    print("[*] Opening the friends page...")
    browser.get(myid+"/friends")
    time.sleep(2)
    print("[*] Scrolling...")
    scroll_to_bottom()
    time.sleep(2)
    myfriends = scan_friends()

    #Write friends to CSV File
    for friend in myfriends:
        writer.writerow([friend['id'],str(friend['name']).encode('utf-8').decode('utf-8'),friend['mutuals']])

    print("[+] Successfully saved to %s" % csvOut)
    end_time = time.time() - start_time
    print("[>] Scrapping took",str(end_time),"s")

    return csvOut
# ---------------> Scrape 2nd degree friends <---------------
#This can take several days if you have a lot of friends!!
def scrape_2nd_degrees():
    start_time = time.time()

    #Prep CSV Output File
    csvOut = 'data/2nd-degree_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'wt', newline='', encoding="utf-8"))
    writer.writerow(['A_id', 'A_name', 'A_mutuals', 'B_id', 'B_name', 'B_mutuals'])

    #Load friends from CSV Input File
    script, filename = argv
    print("[*] Loading list from %s..." % filename)
    myfriends = load_csv(filename)
    print("------------------------------------------")
    for idx,friend in enumerate(myfriends):
        #Load URL of friend's friend page
        scrape_url = "https://m.facebook.com/"+ friend['id'] + "/friends?source_ref=pb_friends_tl"
        browser.get(scrape_url)

        #Scan your friends' Friends page (2nd-degree friends)
        print("%d) %s" % (idx+1, scrape_url))
        scroll_to_bottom()
        their_friends = scan_friends()

        #Write friends to CSV File
        print('[*] Writing friends to CSV...')
        for person in their_friends:
            writer.writerow([friend['id'],friend['name'],friend['mutuals'], person['id'],person['name'],person['mutuals']])

        print("[+] Friend #%d done" % (idx+1))

    print("[+] Successfully saved to %s" % csvOut)
    end_time = time.time() - start_time
    print("[>] Scrapping took",str(end_time),"s")

    return csvOut
# --------------- Check Disconnected Friends ---------------
def who_unfriended_me():
    start_time = time.time()
    #get old frineds and scrape current friends
    #then compare between them
    script, filename, action = argv
    old_friends = load_csv(filename)
    current_friends = load_csv(scrape_1st_degrees())
    # disconnections = [friend for friend in old_friends if friend not in current_friends]

    # remove mutuals column to diff.
    t_current_friends = current_friends
    t_old_friends = old_friends
    for friend in t_current_friends:
        del friend['mutuals']
    for friend in t_old_friends:
        del friend['mutuals']

    # diff
    disconnections = []
    for friend in t_current_friends:
        if friend not in t_old_friends:
            disconnections.append(friend)

    #save to file
    csvOut = 'data/1st-degree-disconnections_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'wt', newline='', encoding="utf-8"))
    writer.writerow(['id', 'name'])
    for friend in disconnections:
        writer.writerow([friend['id'], friend['name']])

    print("[+] Successfully saved to %s" % csvOut)
    end_time = time.time() - start_time
    print("[>] Who Unfriended Me took",str(end_time),"s")
# --------------- 2 Lists Difference ---------------
def friend_list_diff():
    start_time = time.time()
    #get old frineds and scrape current friends
    #then compare between them
    script, filename1, filename2, action = argv
    old_friends = load_csv(filename1)
    current_friends = load_csv(filename2)
    # disconnections = [friend for friend in old_friends if friend not in current_friends]

    # remove mutuals column to diff.
    t_current_friends = current_friends
    t_old_friends = old_friends
    for friend in t_current_friends:
        del friend['mutuals']
    for friend in t_old_friends:
        del friend['mutuals']

    # diff
    disconnections = []
    for friend in t_current_friends:
        if friend not in t_old_friends:
            disconnections.append(friend)

    #save to file
    csvOut = 'data/1st-degree-diff_%s.csv' % now.strftime("%Y-%m-%d_%H%M")
    writer = csv.writer(open(csvOut, 'wt', newline='', encoding="utf-8"))
    writer.writerow(['id', 'name'])
    for friend in disconnections:
        writer.writerow([friend['id'], friend['name']])

    print("[+] Successfully saved to %s" % csvOut)
    end_time = time.time() - start_time
    print("[>] 2 Friend List Difference took",str(end_time),"s")
# ---------------> Vars [2] <---------------
now = datetime.now()
configPath = "config.txt"
# ---------------> Funcs <---------------
def get_config(configPath):
    configObj = configparser.ConfigParser()
    configObj.read(configPath)
    email = configObj.get('credentials', 'email')
    password = configObj.get('credentials', 'password')
    return configObj
def login_from_config():
    fb_login(get_config(configPath))
# ---------------> Main <---------------
def help():
    print("")
    print("===> Help <===")
    print("Use no arguments to scrape your '1st degree connections'.")
    print("Specify the name of the CSV file as the first argument to scrape your '2nd degree connections'.")
    print("Or specify the name of the CSV file as the first argument and 'un' as the second argument to check 'who unfriended you'.")
    print("Or specify the name of the CSV file as the first argument, the name of the second CSV file as the second argument, and 'df' as the third argument to differentiate between 2 lists.")
    print("")

if len(argv) >= 1 and len(argv) <= 3:
    browser = create_browser()

def main():
    full_start_time = time.time()
    print("")
    if len(argv) >= 1 and len(argv) <= 3:
        login_from_config()
    if len(argv) == 1:
        scrape_1st_degrees()
    elif len(argv) == 2:
        scrape_2nd_degrees()
    elif len(argv) == 3:
        script, filename, action = argv
        if action == "un": who_unfriended_me()
    elif len(argv) == 4:
        script, filename1, filename2, action = argv
        if action == "df": friend_list_diff()
    else:
        print("Invalid number of arguments.")
        help()
    print("")
    full_end_time = time.time() - full_start_time
    print("[>] Application took",str(full_end_time),"s")

if __name__ == '__main__':
    main()