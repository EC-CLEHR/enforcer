import chromedriver_autoinstaller
from selenium import webdriver

opt = webdriver.ChromeOptions()
opt.add_argument("--start-maximized")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=opt)
driver.get('https://stackoverflow.com/')