"""Module for asynchronously scraping car auction links from Grays website."""

import asyncio
import random
import pandas as pd
from playwright.async_api import async_playwright

# Base URL and auction page template
BASE_URL = "https://www.grays.com"
AUCTION_URL_TEMPLATE = ("https://www.grays.com/search/automotive-trucks-and-marine/"
                        "motor-vehiclesmotor-cycles?tab=items&sort=close-time-asc&page={}")

# CSV file for storing links
CSV_FILE = 'car_links_to_scrape.csv'

async def main():
    """Main function to scrape car links and update the CSV file."""
    try:
        existing_links = set(pd.read_csv(CSV_FILE)['Car Links'].tolist())
        print(f"Loaded {len(existing_links)} existing links from CSV.")
    except FileNotFoundError:
        existing_links = set()
        print("No existing CSV found. Starting fresh.")

    new_links = set()
    page_number = 1

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        while True:
            auction_url = AUCTION_URL_TEMPLATE.format(page_number)
            print(f"Scraping page {page_number}...")

            try:
                await page.goto(auction_url)
                # Random delay between 2 to 5 seconds
                await asyncio.sleep(random.uniform(2, 5))

                # Collect car links on the current page using XPath
                car_elements = await page.query_selector_all("//a[contains(@href, '/lot/')]")
                if not car_elements:
                    print(f"No more links found. Stopping at page {page_number}.")
                    break

                for element in car_elements:
                    try:
                        link = await element.get_attribute('href')
                        if link and link not in existing_links and link not in new_links:
                            new_links.add(link)
                    except (TypeError, AttributeError) as err:
                        print(f"Error getting link: {err}")

            except (TimeoutError, ValueError) as err:
                print(f"Error loading page {page_number}: {err}")
                break

            page_number += 1

        await browser.close()

    print(f"Found {len(new_links)} new car links.")

    # Update the CSV file with new links only
    if new_links:
        all_links = existing_links.union(new_links)
        links_df = pd.DataFrame(all_links, columns=['Car Links'])
        links_df.to_csv(CSV_FILE, index=False)
        print(f"CSV updated with {len(all_links)} total links.")
    else:
        print("No new links to add to the CSV.")

if __name__ == "__main__":
    asyncio.run(main())
