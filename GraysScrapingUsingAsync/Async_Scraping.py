""" 
Async Web Scraper using Playwright.

This script scrapes car sales data asynchronously using Playwright and 
saves the extracted information into CSV files while avoiding duplicates.
"""

# pylint: disable=invalid-name, broad-exception-caught

import asyncio
import csv
import os
import random
import re
import pandas as pd
from tqdm.asyncio import tqdm
from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth_async

# File paths
CAR_LINKS_FILE = 'car_links_to_scrape.csv'
SOLD_CARS_FILE = 'sold_cars.csv'
SCRAPED_LINKS_FILE = 'scraped_links.csv'

# Initialize CSV files if they don't exist
if not os.path.exists(SOLD_CARS_FILE):
    with open(SOLD_CARS_FILE, 'w', newline='', encoding='utf-8') as file_sold_init:
        writer_sold_init = csv.writer(file_sold_init)
        writer_sold_init.writerow([
            "Year", "Make", "Model", "Title", "Build date",
            "Indicated Odometer Reading", "Fuel Type", "No. of Cylinders",
            "VIN", "URL", "Sold price (AUD)", "Closed date"
        ])

if not os.path.exists(SCRAPED_LINKS_FILE):
    with open(SCRAPED_LINKS_FILE, 'w', newline='', encoding='utf-8') as file_scraped_init:
        writer_scraped_init = csv.writer(file_scraped_init)
        writer_scraped_init.writerow(["URL"])

# Load existing data to avoid duplicates
EXISTING_DATA = pd.read_csv(SOLD_CARS_FILE) if os.path.exists(SOLD_CARS_FILE) else pd.DataFrame()
EXISTING_COMBINATIONS = set(
    zip(EXISTING_DATA['VIN'], EXISTING_DATA['Closed date'])
) if not EXISTING_DATA.empty else set()

# Load the links from CAR_LINKS_FILE
df = pd.read_csv(CAR_LINKS_FILE)
LINKS = df[df.columns[0]].tolist()

# List of user-agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/110.0.0.0 Safari/537.36"
]


def extract_aud_price(sold_price_text):
    """Extract and clean the AUD price from text."""
    match = re.search(r"\$([\d,]+)", sold_price_text)
    return match.group(1).replace(",", "") if match else "N/A"


async def scrape_page(link, browser):
    """Scrape data from a single page asynchronously."""
    try:
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
            device_scale_factor=random.uniform(1.0, 2.0),
            locale="en-US",
            timezone_id="Australia/Sydney"
        )
        page = await context.new_page()
        await stealth_async(page)

        await page.goto(link, timeout=180000, wait_until="load")
        await page.wait_for_selector('body', timeout=5000)

        title = await page.title() or "N/A"

        sold_price_text = (
            await page.locator("text='Sold for'").nth(0).text_content()
            if await page.locator("text='Sold for'").count() > 0 else "N/A"
        )
        sold_price = extract_aud_price(sold_price_text)

        closed_date_element = (
            await page.locator("abbr.endtime").text_content()
            if await page.locator("abbr.endtime").count() > 0 else "N/A"
        )
        closed_date = re.sub(r"\d{2}:\d{2} [A-Z]+", "", closed_date_element).strip()

        if sold_price == "N/A":
            await page.close()
            return None

        details = {
            "Year": "Unknown", "Make": "Unknown", "Model": "Unknown",
            "Title": title, "Build date": "N/A", "Indicated Odometer Reading": "N/A",
            "Fuel Type": "N/A", "No. of Cylinders": "N/A", "VIN": "N/A",
            "URL": link, "Sold price (AUD)": sold_price, "Closed date": closed_date
        }

        try:
            details["Year"], details["Make"], details["Model"] = title.split()[:3]
        except ValueError:
            pass

        elements = await page.locator("ul li").all_text_contents()
        for text in elements:
            if 'Build Date:' in text:
                details["Build date"] = text.split(':')[-1].strip()
            elif 'Indicated Odometer Reading:' in text:
                details["Indicated Odometer Reading"] = text.split(':')[-1].strip()
            elif 'Fuel Type:' in text:
                details["Fuel Type"] = text.split(':')[-1].strip()
            elif 'No. of Cylinders:' in text:
                details["No. of Cylinders"] = text.split(':')[-1].strip()
            elif 'VIN:' in text:
                details["VIN"] = text.split(':')[-1].strip()

        await page.close()

        if (details["VIN"], details["Closed date"]) in EXISTING_COMBINATIONS:
            return None

        return details

    except Exception as err:
        print(f"❌ Error scraping {link}: {err}")
        return None


CONCURRENCY_LIMIT = 20


async def limited_scrape_page(link, browser, semaphore):
    """Ensure controlled concurrency when scraping pages."""
    async with semaphore:
        return await scrape_page(link, browser)


async def process_links():
    """Process all links asynchronously with concurrency control."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        tasks = [limited_scrape_page(link, browser, semaphore) for link in LINKS]

        results = []
        for future in tqdm(asyncio.as_completed(tasks), total=len(tasks),
                           desc="Processing Links", unit="link"):
            result = await future
            if result:
                results.append(result)

        await browser.close()

    with open(SOLD_CARS_FILE, 'a', newline='', encoding='utf-8') as sold_handle:
        sold_writer = csv.writer(sold_handle)
        for row in results:
            sold_writer.writerow(row.values())

    with open(SCRAPED_LINKS_FILE, 'a', newline='', encoding='utf-8') as scraped_handle:
        scraped_writer = csv.writer(scraped_handle)
        for row in results:
            scraped_writer.writerow([row["URL"]])

    scraped_urls = {row["URL"] for row in results}
    updated_df = df[~df[df.columns[0]].isin(scraped_urls)]
    updated_df.to_csv(CAR_LINKS_FILE, index=False)


asyncio.run(process_links())

print("✅ Scraping completed.")
