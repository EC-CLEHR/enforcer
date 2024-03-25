from selenium.webdriver.common.by import By
from selenium import webdriver
import chromedriver_autoinstaller


chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

driver = webdriver.Chrome()
driver.get("http://www.python.org")
assert "Python" in driver.title

url = 'https://devccm.enablecomp.com/'

def test_contactUs():
    driver.get(url)
    #contact_us_link = WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Contact Us')))
    button = driver.find_element(By.LINK_TEXT, 'Contact Us');
    button.click()
    driver.quit()
