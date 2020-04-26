from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as cond
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import argparse
import os, zipfile, shutil
import platform
import sys
import time

# Global Constants.
MOODLE_URL = "https://moodle.rose-hulman.edu/login/index.php"
DOWNLOAD_DIR = "C:\\Users\\eckelsjd\\source\\repos\\SeleniumProjects\\PDFdownload\\downloads"
ZIP_EXT = ".zip"
username_KEY = "username"
PASSWORD_KEY = "password"
COURSE_KEY = "course"
TERM_KEY = "term"

def append_exe_if_needed(os_name, driver_path):
    if (os_name == "Darwin"):
        return driver_path
    return driver_path + ".exe"

def get_driver(browser):
    """
        Gets the driver for the specified browser

        Arguments:
            :type browser       String
                browser webdriver to return.

        Returns the Webdriver for the specified browser.
    """
    os_name = platform.system()
    if (browser == "chrome"):
        driver_path = append_exe_if_needed(os_name, "./drivers/chromedriver")
        chrome_options = webdriver.ChromeOptions()

        # Set chrome options to immediately download pdfs; disable Chrome PDF Viewer
        prefs = {}
        prefs["download.default_directory"] = DOWNLOAD_DIR
        prefs["download.prompt_for_download"] = False
        prefs["download.directory_upgrade"] = True
        prefs["plugins.plugins_list"] = [{"enabled":False,"name":"Chrome PDF Viewer"}]
        prefs["download.extensions_to_open"] = "applications/pdf"
        prefs["profile.default_content_settings.popups"] = 0;
        prefs["plugins.always_open_pdf_externally"] = True

        chrome_options.add_experimental_option("prefs",prefs)
        return webdriver.Chrome(driver_path,
                                service_log_path="./logs/chrome.log",chrome_options=chrome_options)
    elif (browser == "phantom"):
        driver_path = append_exe_if_needed(os_name, "./drivers/phantomjs")
        return webdriver.PhantomJS(driver_path,
                                   service_log_path="./logs/phantom.log")
    elif (browser == "firefox"):
        driver_path = append_exe_if_needed(os_name, "./drivers/geckodriver")
        return webdriver.Firefox(executable_path=driver_path,
                                 log_path="./logs/firefox.log")
    else:
        print("Invalid option...using PhantomJS")
        driver_path = append_exe_if_needed(os_name, "./drivers/phantomjs")
        return webdriver.PhantomJS(driver_path,
                                   service_log_path="./logs/phantom.log")

def setup_directory():
    """
        Creates the logs and img files if not created.
    """
    # Make directory for logs and images if necessary.
    if (not os.path.isdir("./logs/")):
        os.makedirs("./logs/")
    if (not os.path.isdir("./img/")):
        os.makedirs("./img/")
    if (not os.path.isdir("./downloads/")):
        os.makedirs("./downloads/")

def get_data(data_file):
    """
        Pulls user data from data.txt.

        Arguments:
            :type data_file     String
                Path String to data text.

        Returns a dictionary of relevant data.
    """
    data_file = open(data_file, "r")
    dataMap = {}

    for line in data_file:
        lineList = line.split()
        dataMap[lineList[0]] = lineList[1:len(lineList)]

    data_file.close()

    return dataMap

def parse_arguments():
    """
        Returns the arguments parsed from the command line.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--data", help="Data text file file path", required=True)
    parser.add_argument(
        "-b", "--browser", help="Webdriver to use", default="phantom", required=True)

    return parser.parse_args()

def click_tag_with_value(driver, tag_name, value):
    """
       Attempts to click on a button with a specific tag name and value.
       It will click the first button with specified value.

       Arguments:
           :type driver :     webdriver
               Selenium Webdriver.
           :type tag_name :    str
               Specified HTML tag name.
           :type value :      str
               Specified HTML value related to tag name.

        Returns nothing.
    """
    inputList = driver.find_elements_by_tag_name(tag_name)

    for element in inputList:
        if (element.get_attribute("value") == value):
            element.click()
            break

def login(driver, username, password):
    """
        Login to Moodle.

        Arguments:
            :type driver :        webdriver
                Selenium Webdriver.
            :type username :      String
                Rose-Hulman username.
            :type password :      String
                Rose-Hulman password.
    """
    # Navigate to Moodle.
    driver.get(MOODLE_URL)

    # Login to Moodle
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").send_keys(password)
    button = driver.find_element_by_id("loginbtn")
    button.click()

def navigate_to_class_page(driver, course):
    """
        Navigates to the desired course page.

        Arguments:
            :type driver        webdriver
                Selenium Webdriver.
            :type course           String
                Rose-Hulman course number
                Example: '1920W ME327-03'
    """
    # Finds the xpath of the WebElement that links to the course moodle page
    xpath = "//*[text()='" + course + "']//ancestor::a[1]"
    page = driver.find_element_by_xpath(xpath)
    page.click()

def download_pdfs(driver):
    """
        Finds and downloads all pdfs on a moodle class page

        Arguments:
            :type driver        webdriver
                Selenium Webdriver.
    """
    # Path to all 'a' tagged embedded links in the 'topics' list
    xpath = "//ul[@class='topics']//child::a"
    elements = driver.find_elements_by_xpath(xpath)

    # Scan all links for 'resources' and 'folders'
    # This should pick up all pdf files, and ignore all other junk links
    # By inspection, links on moodle follow this format: https://moodle.rose-hulman.edu/mod/x/view.php?id=y
    # where x = resource, folder, or url; x occurs at index 4 with split('/') command
    # and   y = some id number

    for element in elements:
        # Ensure all elements on xpath are loaded to avoid Stale Element Exception
        wait = WebDriverWait(driver,10)
        wait.until(cond.visibility_of_all_elements_located((By.XPATH,xpath)))

        # Access the link
        link = element.get_attribute("href")
        link_items = link.split('/')

        # Finds all links to resource files
        if ((link_items[4] == "resource") or (link_items[4] == "folder")):
            windows_before = driver.current_window_handle

            # Open and switch to link in new tab
            driver.execute_script("window.open('%s')" % link)
            WebDriverWait(driver, 10).until(cond.number_of_windows_to_be(2))
            windows_after = driver.window_handles
            new_window = [x for x in windows_after if x != windows_before][0]

            # Switching to a new tab will auto-download pdf files and close the
            # window under the current chrome settings
            driver.switch_to_window(new_window)

            # If the window doesn't close, then it wasn't a pdf file; skip past it or open folder; wait 1 second
            try:
                WebDriverWait(driver, 1).until(cond.number_of_windows_to_be(1))
                driver.switch_to_window(windows_before)
            except TimeoutException as e:
                if (link_items[4] == "folder"):
                    btn_xpath = "//section[@id='region-main']//child::button[1]"
                    WebDriverWait(driver,10).until(cond.element_to_be_clickable((By.XPATH,btn_xpath)))
                    dwnld_btn = driver.find_element_by_xpath(btn_xpath)
                    dwnld_btn.click()
                    driver.close()
                    driver.switch_to_window(windows_before)
                else:
                    print("Found non-pdf file. Skipping. . .")
                    driver.close()
                    driver.switch_to_window(windows_before)
                    pass

def unzip():
    """
        Finds and unzips all zip files in download directory

        Arguments:
            :NONE
            :ASSUMES global values:
            DOWNLOAD_DIR -> location of download directory
            ZIP_EXT -> file extension of the zip files to extract
    """
    os.chdir(DOWNLOAD_DIR)
    for item in os.listdir(DOWNLOAD_DIR):
        if item.endswith(ZIP_EXT):
            filename = os.path.abspath(item)
            zip_ref = zipfile.ZipFile(filename)
            zip_ref.extractall(DOWNLOAD_DIR)
            zip_ref.close()
            os.remove(filename)

def organize_dir():
    """
        Organizes download directory by file extension

        Arguments:
            :NONE
            :ASSUMES global values:
            DOWNLOAD_DIR -> location of download directory
    """
    # get all file extensions in the folder
    ext_set = set()
    os.chdir(DOWNLOAD_DIR)
    for item in os.listdir(DOWNLOAD_DIR):
        filename = os.path.abspath(item)
        split_file = os.path.splitext(filename) # returns tuple
        ext = split_file[1] # get the file extension
        ext_trim = ext[1:] # trim off the period
        if not ext_trim in ext_set:
            ext_set.add(ext_trim)

    # initialize dictionary with empty lists
    files = {new_list: [] for new_list in ext_set}

    # group files in dictionary by file extension
    for item in os.listdir(DOWNLOAD_DIR):
        filename = os.path.abspath(item)
        split_file = os.path.splitext(filename) # returns tuple
        ext = split_file[1] # get the file extension
        ext_trim = ext[1:]
        files[ext_trim].append(filename)

    # create and fill directories based on file extension
    for key in files:
        if not key == '':
            os.makedirs("%s" % key)
            for file in files[key]:
                shutil.move(file,"./%s" % key)

def main():
    """
        Driver Function.
    """
    # Get arguments and setup.
    arguments = parse_arguments()
    setup_directory()

    # Initialize Data.
    data_map = get_data(arguments.data)

    # Initialize Webdriver.
    driver = get_driver(arguments.browser.lower())

    # Login to moodle
    login(driver, data_map[username_KEY], data_map[PASSWORD_KEY])

    # Navigate to class page
    # Remember: data_map stores its values as lists; We only want the 1st index
    course_num = data_map[TERM_KEY][0] + " " + data_map[COURSE_KEY][0]
    navigate_to_class_page(driver, course_num)

    # Download all pdfs on class page
    download_pdfs(driver)

    # Unzip all folders
    unzip()

    # Organize directory by file type
    organize_dir()

    # Close the driver if it is the PhantomJS driver.
    # Otherwise, leave the webdriver open for user manual overrides.
    if (isinstance(driver, webdriver.PhantomJS)):
        driver.close()
    else:
        print("Waiting For User to terminate (Ctrl-C)")
        while(True):
            pass

if __name__ == "__main__":
    main()