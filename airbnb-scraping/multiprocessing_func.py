import time
import pandas as pd
from pandas import DataFrame
import urllib.parse as urlparse
from urllib.parse import parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# helper func to scrape comments
def scrape_comments(driver):
    comments = []
    XPATH_COMMENTS_BTN = "//button[contains(@aria-label, 'Bewertungen anzeigen, Öffnet den Modaldialog.')]"
    XPATH_COMMENTS_BTN_CLOSE = "//button[@aria-label='Schließen']"
    XPATH_COMMENTS_CLASS = "span[class='ll4r2nl dir dir-ltr']"
    XPATH_COMMENTS_ON_SITE = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[3]/div/div/*"

    try:
        WebDriverWait(driver, 4).until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]")))
    except:
        print("could not load comments title")
        return comments

    try:
        if driver.find_elements(By.XPATH, XPATH_COMMENTS_BTN):
            driver.find_element(By.XPATH, XPATH_COMMENTS_BTN).click()
            WebDriverWait(driver, 4).until(EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@data-testid, 'pdp-reviews-modal-scrollable-panel')]")))
            resu = driver.find_elements(By.CSS_SELECTOR, XPATH_COMMENTS_CLASS)
            for comm in resu:
                if comm.text:
                    comments.append(comm.text)
            driver.find_element(By.XPATH, XPATH_COMMENTS_BTN_CLOSE).click()

        elif not driver.find_elements(By.XPATH, XPATH_COMMENTS_BTN) and len(driver.find_elements(By.XPATH, XPATH_COMMENTS_ON_SITE)) > 0:
            comments_on_page = driver.find_elements(
                By.XPATH, XPATH_COMMENTS_ON_SITE)
            for comm_on in comments_on_page:
                if comm_on.text:
                    temp_comm_on = comm_on.text.split("\n", maxsplit=2)[2:]
                    comments.append(temp_comm_on[0])

        else:
            return comments

    except:
        print("could not process comments")
        return comments

    return comments

# helper func to scrape coordinates
def scrape_coordinates(driver):
    lat = 0.0
    lng = 0.0

    try:
        element_to_be_present_co = WebDriverWait(driver, 4).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[5]/div/div/div/div[2]/section/div[1]/div/h2")))
        driver.execute_script("arguments[0].scrollIntoView();", element_to_be_present_co)

        time.sleep(1)

        coordinates_elem = WebDriverWait(driver, 4).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(@href, 'https://maps.google.com/maps?ll=')]")))
        coordinates_href = coordinates_elem.get_attribute('href')

        parsed_href = urlparse.urlparse(coordinates_href)
        coordinates = parse_qs(parsed_href.query)['ll'][0].split(',')
        lat = float(coordinates[0])
        lng = float(coordinates[1])
    except:
        print("Could not process coordinates")

    return lat, lng

# helper func to scrape ameneties
def scrape_ameneties(driver):

    ameneties_list = []

    try:
        SHOW_AMENETIES_CLASS = "button[class='l1j9v1wn b65jmrv v7aged4 dir dir-ltr']"
        driver.find_element(By.CSS_SELECTOR, SHOW_AMENETIES_CLASS).click()

        element_present_ame = EC.presence_of_element_located(
            (By.XPATH, "//div[@aria-label='Das bietet dir diese Unterkunft']"))
        WebDriverWait(driver, 6).until(element_present_ame)

        soup = BeautifulSoup(driver.page_source, features='html.parser')
        ameneties = soup.find_all("div", {"class": "t1dx2edb dir dir-ltr"})

        for a in ameneties:
            if "</span>" not in a.decode_contents():
                ameneties_list.append(a.decode_contents())

    except:
        print("Could not process ameneties")

    try:
        driver.find_element(
            By.XPATH, "//button[@aria-label='Schließen']").click()
    except:
        print("Could not close ameneties window")

    return ameneties_list

# scrapping logic for detail page apartment
def scrape_apartment(nr_of_flat, driver):

    flat = None

    XPATH_cleanliness = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[1]/div/div/div[2]/span"
    XPATH_communication = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[3]/div/div/div[2]/span"
    XPATH_checkin = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[5]/div/div/div[2]/span"
    XPATH_valueformoney = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[6]/div/div/div[2]/span"
    XPATH_location = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[4]/div/div/div[2]/span"
    XPATH_data_accuracy = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[2]/div/div/div[2]/div/div/div[2]/span"
    rating_cleanliness = ""
    rating_communication = ""
    rating_checkin = ""
    rating_valueformoney = ""
    rating_location = ""
    rating_data_accuracy = ""

    XPATH_APARETMENT_NAME = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[1]/span/h1"
    apartment_name = ""

    XPATH_PRICE = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/span/div/span[1]"
    apartment_price = ""
    XPATH_PRICE_REDUCED = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/span/div/span[2]"
    apartment_price_reduced = ""

    XPATH_PLACE = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[3]/button/span"
    XPATH_PLACE_2 = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[5]/button/span"
    apartment_place = ""

    XPATH_RATING = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[2]"
    rating = ""

    XPATH_GUESTS = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/ol/li[1]/span[1]"
    guests = ""
    XPATH_BEDROOMS = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/ol/li[2]/span[2]"
    bedrooms = ""
    XPATH_BEDS = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/ol/li[3]/span[2]"
    beds = ""
    XPATH_BATHROOMS = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div/div[1]/ol/li[4]/span[2]"
    bathrooms = ""

    XPATH_NR_OF_RATINGS = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[2]/div[1]/span[1]/span[3]/button"
    nr_of_ratings = ""

    # check if page title is present
    try:
        element_present = EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[1]/div[1]/div/div/div/div/section/div[1]/span/h1"))
        WebDriverWait(driver, 8).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        return

    try:
        if driver.find_elements(By.XPATH, XPATH_PLACE):
            apartment_place = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, XPATH_PLACE))).text
            if "Zürich" not in apartment_place:
                return flat
        else:
            apartment_place = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, XPATH_PLACE_2))).text
            if "Zürich" not in apartment_place:
                return flat
    except:
        pass

    try:
        apartment_name = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, XPATH_APARETMENT_NAME))).text
        nr_of_ratings = WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located((By.XPATH, XPATH_NR_OF_RATINGS))).text
    except:
        pass

    try:
        apartment_price = WebDriverWait(driver, 4).until(
            EC.visibility_of_element_located((By.XPATH, XPATH_PRICE))).text

        if driver.find_elements(By.XPATH, XPATH_PRICE_REDUCED):
            apartment_price_reduced = driver.find_element(
                By.XPATH, XPATH_PRICE_REDUCED).text
            if "CHF" not in apartment_price_reduced:
                apartment_price_reduced = ""
    except:
        pass

    try:
        rating = driver.find_element(By.XPATH, XPATH_RATING).text
        rating_checkin = driver.find_element(By.XPATH, XPATH_checkin).text
        rating_cleanliness = driver.find_element(
            By.XPATH, XPATH_cleanliness).text
        rating_communication = driver.find_element(
            By.XPATH, XPATH_communication).text
        rating_data_accuracy = driver.find_element(
            By.XPATH, XPATH_data_accuracy).text
        rating_location = driver.find_element(By.XPATH, XPATH_location).text
        rating_valueformoney = driver.find_element(
            By.XPATH, XPATH_valueformoney).text
    except:
        pass

    try:
        guests = driver.find_element(By.XPATH, XPATH_GUESTS).text
        bedrooms = driver.find_element(By.XPATH, XPATH_BEDROOMS).text
        beds = driver.find_element(By.XPATH, XPATH_BEDS).text
        bathrooms = driver.find_element(By.XPATH, XPATH_BATHROOMS).text
    except:
        pass

    apartment_ameneties = scrape_ameneties(driver)
    comments = scrape_comments(driver)
    lat, lng = scrape_coordinates(driver)

    flat = {'name': [apartment_name], 'price': [apartment_price], 'price_reduced': [apartment_price_reduced], 'place': [apartment_place], 'guests': [guests], 'bedrooms': [bedrooms], 'beds': [beds], 'bathrooms': [bathrooms], 'lat': [lat], 'lng': [lng], 'nr_of_ratings': [nr_of_ratings], 'rating_overall': [rating], 'rating_valueformoney': [rating_valueformoney],
            'rating_location': [rating_location], 'rating_checkin': [rating_checkin], 'rating_communication': [rating_communication], 'rating_cleanliness': [rating_cleanliness], 'rating_data_accuracy': [rating_data_accuracy], 'comments': [comments], 'list_ameneties': [apartment_ameneties]}

    print(nr_of_flat)

    return flat

def close_tab(driver):
    try:
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
    except:
        print("could not close tab")

# helper func to open each aparement in sepeerate tab
def handle_apartments_tabs(nr_apartments, driver):
    # Click on each apartment which is opened in seperate tab
    apartments = pd.DataFrame()
    for nr in range(1, nr_apartments):
        xpath = f"/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/main/div[2]/div[2]/div/div/div/div/div/div[{nr}]"
        driver.find_element(By.XPATH, xpath).click()

        try:
            time.sleep(1)
            # switch to new tab
            driver.switch_to.window(driver.window_handles[-1])
        except:
            print("could not switch tab")
            continue

        try:
            # close translate banner
            transl = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Schließen']")))
            transl.click()
        except:
            pass

        apartment_scraped = scrape_apartment(nr, driver)

        if apartment_scraped == None:
            close_tab(driver)
            continue

        apartments = pd.concat([apartments, pd.DataFrame(apartment_scraped)])
        close_tab(driver)

    return apartments


def run_scraping(airbnb_url_to_scrape) -> DataFrame:
    opts = Options()
    #opts.add_argument("--window-size=1200,800")
    opts.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.get(airbnb_url_to_scrape)

    time.sleep(2)

    # wait till cookie banner pops up
    try:
        # close cookie banner
        cookie = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html[@class='js-focus-visible']/body[@class='with-new-header']/div[5]/div/div/div/div[1]/div[3]/section/div[2]/div[2]/button"))) 
        cookie.click()
    except:
        pass

    # get nr of pages with aparements
    nav_buttons_pages = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/main/div[2]/div[3]/div/div/nav/div/*")
    try:
        # get nr of pages
        nr_pages = int(nav_buttons_pages[(len(nav_buttons_pages)-2)].text)
    except:
        nr_pages = 1
    
    # get entries of apparements on page
    nr_apartments = len(driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/main/div[2]/div[2]/div/div/div/div/div/div"))

    # limited entries for tests 
    scraped_apartments = pd.DataFrame()
    XPATH_NEXT_PAGE = "//a[@aria-label='Weiter']"
    XPATH_WAIT_TILL_ELEM_VISIBLE = "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div/div/div[2]/main/div[2]/div[2]/div/div/div/div/div/div[1]"

    for nr_p in range(1, nr_pages):
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, XPATH_WAIT_TILL_ELEM_VISIBLE)))
        temp_pd = handle_apartments_tabs(nr_apartments + 1, driver)
        scraped_apartments = pd.concat([scraped_apartments, temp_pd])
        driver.find_element(By.XPATH, XPATH_NEXT_PAGE).click()
    
    # close all tabs and window
    for handles in driver.window_handles:
        parent = handles
        driver.switch_to.window(parent)
        driver.close()

    return scraped_apartments
