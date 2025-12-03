# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def upload_file(path):
    driver = webdriver.Chrome()
    driver.get("https://yourwebsite.com/login")

    # login
    driver.find_element(By.ID, "username").send_keys("YOUR_USERNAME")
    driver.find_element(By.ID, "password").send_keys("YOUR_PASSWORD")
    driver.find_element(By.ID, "login-button").click()
    time.sleep(2)

    # go to upload section
    driver.get("https://yourwebsite.com/upload-page")

    # upload
    upload_element = driver.find_element(By.NAME, "fileUpload")
    upload_element.send_keys(path)

    driver.find_element(By.ID, "submit").click()
    time.sleep(2)
    driver.quit()
