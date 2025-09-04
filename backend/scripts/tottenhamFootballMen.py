from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from datetime import datetime
from pathlib import Path
import os
import sys
import time
import platform


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

        today = datetime.now()
        assumed_year = today.year
        fixture_date = datetime(assumed_year, month, dayNumber)
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

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-zygote")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--hide-scrollbars")

    opts.page_load_strategy = "eager"

    driver = None
    try:
        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(30)

        driver.get("https://www.tottenhamhotspur.com/fixtures/men/")

        wait = WebDriverWait(driver, 20)

        try:
            wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
        except TimeoutException:
            pass

        fixtureGroups = wait.until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "FixtureGroup"))
        )

        for group in fixtureGroups:
            fixtureItems = group.find_elements(By.CLASS_NAME, "FixtureItem ")
            for fixture in fixtureItems:
                match = fixture.get_attribute("title")

                scoresText = fixture.find_element(By.CLASS_NAME, "scores").get_attribute("innerHTML")
                if scoresText != "VS":
                    continue
                try:
                    fixtureDesktop = fixture.find_element(By.CLASS_NAME, "FixtureItem__desktop")
                    fixtureDesktopWrapper = fixtureDesktop.find_element(By.CLASS_NAME, "wrapper")
                    _homeGameTest = fixtureDesktopWrapper.find_element(
                        By.CSS_SELECTOR, ".stadium-tag.stadium-tag--home"
                    )
                    fixtureItemKickOffTime = fixtureDesktopWrapper.find_element(By.CLASS_NAME, "FixtureItem__kickoff")
                    fixtureDay = fixtureItemKickOffTime.find_element(By.TAG_NAME, "p").text
                    fixtureItemKickOffTimeText = fixtureItemKickOffTime.text
                    fixtureDate = fixtureItemKickOffTimeText.splitlines()[1]
                    formattedDate, formattedTime = formatDateTime(fixtureDate, fixtureDay)

                    abbreviationsAsText = []
                    abbreviations = fixtureDesktopWrapper.find_element(
                        By.CLASS_NAME, "FixtureItem__crests"
                    ).find_elements(By.TAG_NAME, "p")
                    for abbreviation in abbreviations:
                        abbreviationsAsText.append(abbreviation.text)

                    arrayToAppend = ["Football", match, formattedDate, formattedTime, abbreviationsAsText]
                    finalEvents.append(arrayToAppend)
                except Exception:
                    # skip malformed/played items silently (same as your original)
                    pass

    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    return finalEvents
