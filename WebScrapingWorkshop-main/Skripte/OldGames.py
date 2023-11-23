from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep 
driver = webdriver.Chrome()
base = "https://boardgamearena.com/table?table="
urls = [base + str(310000000 + i) for i in range(0, 120000000)]
urllist = []
for url in urls:
    driver.get(url)
    try: 
        name = driver.find_element("id", "table_name")
        if name.text == "Just One":
            urllist.append(url)
    except: 
        pass
    sleep(2)
driver.quit()
print(urllist)