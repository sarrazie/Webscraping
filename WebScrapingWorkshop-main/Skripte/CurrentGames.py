from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep 
from bs4 import BeautifulSoup
import re
import urllib.request
import urllib.error
import pandas as pd
from datetime import datetime
import schedule

def Current_Games():
    driver = webdriver.Chrome()
    username= 'erik.sarrazin@t-online.de'
    password= 'Borussia1900'
    driver.get('https://de.boardgamearena.com/account?redirect=account?redirect=gameinprogress?game=1533&all')
    driver.find_element("id", "username_input").send_keys(username)
    driver.find_element("id", "password_input").send_keys(password)
    driver.find_element("id", "submit_login_button").click()
    sleep(5)
    url = "https://boardgamearena.com/gameinprogress?game=1533&all"
    driver.get(url)
    sleep(5)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    sleep(5)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    driver.quit()

    soup = BeautifulSoup(html,'lxml')
    data = str(soup)
    links = soup.find_all('a', class_='gametablelink')
    urls = re.findall(r'href="([^"]+)"', str(links))
    print(urls)
    i=0
    df= pd.DataFrame()
    ids = pd.Series(['Table Number', 'Move', 'Mode', 'Speed', 'Language', 'End', 'Clues', 'Mystery Word', 'Guess'], name = 'ids')
    for url in urls:
        try:
            with urllib.request.urlopen(url) as response:
                html = response.read()
        except urllib.error as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
            else:
                pass
        soup = BeautifulSoup(html,'lxml')
        data = str(soup)

        pattern = r'"guess":"([^"]*)"'

        if re.search(pattern, data):
            meta_tag = soup.find('meta', {'property': 'og:url'})
            content = meta_tag['content']
            table_nbr = content.split('=')[-1]
            print(table_nbr)

            pattern_moves = r'"move_nbr":"(.*?)"'
            moves = re.findall(pattern_moves, data)
            for move in moves:
                print(move)

            pattern_mode = r'"menu_option_value_201">(.*?)<'
            modes = re.findall(pattern_mode, data)
            for mode in modes:
                print(mode)

            pattern_speed = r'"menu_option_value_200">(.*?)<'
            speeds = re.findall(pattern_speed, data)
            for speed in speeds:
                print(speed)
            
            pattern_language = r'"menu_option_value_207">(.*?)<'
            languages = re.findall(pattern_language, data)
            for language in languages:
                print(language)

            pattern_end = r'"menu_option_value_100">(.*?)<'
            ends = re.findall(pattern_end, data)
            for end in ends:
                print(end)

            pattern_clues = r'"clueText":"(.*?)"'
            clue_texts = re.findall(pattern_clues, data)

            for clue_text in clue_texts:
                print(clue_text)

            pattern_mystery = r'"mystery_word":"(.*?)"'
            mystery_words = re.findall(pattern_mystery, data)
            for mystery in mystery_words:
                print(mystery)

            pattern_guesses = r'"guess":"(.*?)"'
            guesses = re.findall(pattern_guesses, data)
            for guess in guesses:
                print(guess)
            i= i+1
            rounds= pd.Series([table_nbr, moves, mode, speed, language, end, clue_texts, mystery_words[0], guesses[0]], name= 'Scrapnumber' + str(i))
            df = pd.concat([df, rounds], axis=1)
        else: 
            pass
        sleep(5)
    df = pd.concat([ids, df], axis=1)
    filename = ('Game_data_' + datetime.now().strftime("%Y-%m-%d-%H-%M") + '.csv')
    df.to_csv(filename, index=False)

schedule.every(2).hours.do(Current_Games)

while 1:
    schedule.run_pending()
    sleep(1)