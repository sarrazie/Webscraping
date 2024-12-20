import pandas as pd
from datetime import datetime
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import re
import urllib.request
from urllib3.exceptions import MaxRetryError, NewConnectionError, ConnectionError
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


def Current_Games():
    try:
        driver = webdriver.Chrome(options=options)
        username = 'erik.sarrazin@t-online.de'
        password = 'Borussia1900'
        driver.get('https://de.boardgamearena.com/account?redirect=account?redirect=gameinprogress?game=1533&all')
        driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[10]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[2]/div/input").send_keys(username)
        sleep(2)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[10]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[2]/form/div[3]/div/a").click()
        sleep(2)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[10]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[1]/div[2]/div/input").send_keys(password)
        sleep(2)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[10]/div[3]/div/div[2]/div/div[2]/div[2]/div/form/div[2]/div/div/a").click()
        sleep(2)
        driver.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div/div/div/div[10]/div[3]/div/div[2]/div/div[2]/div[3]/div[2]/div[3]/div[3]/div/div/a").click()
        sleep(5)
        url = "https://boardgamearena.com/gameinprogress?game=1533&all"
        driver.get(url)
        sleep(2)
        element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#main-content > div > div.flex.items-center.justify-center.gap-2 > div:nth-child(4) > div > div > a")))
        urls = []
        while True:
            try:
                driver.execute_script("window.scrollTo(0, 0);")
                sleep(1)
                scroll_step = 500
                page_height = driver.execute_script("return document.body.scrollHeight")
                scroll_position = 0
                while scroll_position < page_height:
                    driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_step)
                    scroll_position += scroll_step
                    sleep(1)
                html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
                soup = BeautifulSoup(html, 'lxml')
                data = str(soup)
                link_tags = soup.find_all('a', class_='absolute inset-0 block')
                for tag in link_tags:
                    urls.append(tag['href'])
                element = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#main-content > div > div.flex.items-center.justify-center.gap-2 > div:nth-child(4) > div > div > a")))
                element.click()
            except TimeoutException:
                break
        driver.quit()
        print(urls)
        i = 0
        df = pd.DataFrame()
        ids = pd.Series(['Table Number', 'Move', 'Mode', 'Speed', 'Language', 'End', 'Clues', 'Mystery Word', 'Guess'],
                        name='ids')
        for url in urls:
            url = 'https:' + url
            try:
                with urllib.request.urlopen(url) as response:
                    html = response.read()
                soup = BeautifulSoup(html, 'lxml')
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
                    i = i + 1
                    rounds = pd.Series(
                        [table_nbr, moves, mode, speed, language, end, clue_texts, mystery_words[0], guesses[0]],
                        name='Scrapnumber' + str(i))
                    df = pd.concat([df, rounds], axis=1)
                else:
                    pass
            except (MaxRetryError, NewConnectionError, ConnectionError) as e:
                print("Error:", e)
            except Exception as e:
                print("An unexpected error occurred:", e)
            sleep(5)
        df = pd.concat([ids, df], axis=1)
        filename = ('Game_data_' + datetime.now().strftime("%Y-%m-%d-%H-%M") + '.csv')
        df.to_csv(filename, index=False)
    except Exception as e:
        print("An unexpected error occurred:", e)


schedule.every(4).hours.do(Current_Games)

while 1:
    schedule.run_pending()
    sleep(1)
