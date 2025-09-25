from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from datetime import datetime
from datetime import datetime
from zoneinfo import ZoneInfo

def formatDateTime(date, day):
    months = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }
    try:
        dayNumberAndMonth, timePart = date.split(",")
        dayNumber, monthStr = dayNumberAndMonth.split()
        dayNumber = int(dayNumber)
        month = months[monthStr.upper()]
        
        today = datetime.now(ZoneInfo("Europe/London"))
        assumed_year = today.year
        fixture_date = datetime(assumed_year, month, dayNumber, tzinfo=ZoneInfo("Europe/London"))
        if fixture_date < today:
            fixture_date = datetime(assumed_year + 1, month, dayNumber)

        formattedDate = f"{day} {dayNumber:02d} {fixture_date.strftime('%B')} {fixture_date.year}"
        formattedTime = timePart.strip()
        return formattedDate, formattedTime

    except Exception as e:
        print(f"Error in format_date_time: {e}")
        return None, None


def tottenhamFootballMen():
    finalEvents = []

    #Set up driver, visit website and bypass cookies button
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.page_load_strategy = "none"
    driver = webdriver.Chrome(options=options)  
    driver.set_page_load_timeout(120)
    driver.get('https://www.tottenhamhotspur.com/fixtures/men/')
    wait = WebDriverWait(driver, 120)
    wait.until(EC.element_to_be_clickable((By.ID,'onetrust-accept-btn-handler'))).click()


    fixtureGroups = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"FixtureGroup")))
    for group in fixtureGroups:
        fixtureItems = group.find_elements(By.CLASS_NAME, "FixtureItem")
        for fixture in fixtureItems:
            match = fixture.get_attribute("title")

            #Figure out if it's been played or not
            scoresText = fixture.find_element(By.CLASS_NAME,"scores").get_attribute("innerHTML")
            if scoresText != "VS":
                continue
            try:
                #Extract kick off date and time
                fixtureDesktop = fixture.find_element(By.CLASS_NAME, 'FixtureItem__desktop')
                fixtureDesktopWrapper = fixtureDesktop.find_element(By.CLASS_NAME, 'wrapper')
                homeGameTest = fixtureDesktopWrapper.find_element(By.CSS_SELECTOR, '.stadium-tag.stadium-tag--home')
                fixtureItemKickOffTime = fixtureDesktopWrapper.find_element(By.CLASS_NAME, 'FixtureItem__kickoff')
                fixtureDay = fixtureItemKickOffTime.find_element(By.TAG_NAME, 'p').text
                fixtureItemKickOffTimeText = fixtureItemKickOffTime.text
                fixtureDate = fixtureItemKickOffTimeText.splitlines()[1]
                formattedDate, formattedTime = formatDateTime(fixtureDate, fixtureDay)
                
                #Extract abbreviations for the teams playing
                abbreviationsAsText = []
                abbreviations = fixtureDesktopWrapper.find_element(By.CLASS_NAME, 'FixtureItem__crests').find_elements(By.TAG_NAME, "p")
                for abbreviation in abbreviations:
                    abbreviationsAsText.append(abbreviation.text)

                arrayToAppend = ["Football",match, formattedDate, formattedTime,abbreviationsAsText]
                finalEvents.append(arrayToAppend)
            except Exception as e:
                pass

    driver.quit()
    return finalEvents
