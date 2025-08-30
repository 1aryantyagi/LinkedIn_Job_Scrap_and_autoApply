import asyncio
import csv
import json
import os
import time
import logging
from playwright.async_api import async_playwright
import random

from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

class LinkedInPostScraperPlaywright:
    def __init__(self, email=EMAIL, password=PASSWORD, headless=False):
        self.EMAIL = email
        self.PASSWORD = password
        self.headless = headless
        self.page = None
        self.browser = None
        self.post_links = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.page = await self.browser.new_page()
            
            
            self.logger.info("Browser started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise
    
    async def login_to_linkedin(self):
        """Login to LinkedIn with provided credentials"""
        try:
            self.logger.info("Navigating to LinkedIn login page")
            await self.page.goto("https://www.linkedin.com/login")
            
            # Wait for login form
            await self.page.wait_for_selector("#username", timeout=10000)
            
            # Enter credentials
            await self.page.fill("#username", self.email)
            await self.page.fill("#password", self.password)
            
            # Click login button
            await self.page.click("button[type='submit']")
            
            # Wait for successful login
            await self.page.wait_for_selector(
                ".search-global-typeahead, .feed-container-theme",
                timeout=15000
            )
            
            self.logger.info("Successfully logged into LinkedIn")
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise
    
    async def search_hashtags(self, hashtags):
        """Search for hashtags on LinkedIn"""
        try:
            search_query = " ".join(hashtags)
            self.logger.info(f"Searching for: {search_query}")
            
            # Find and use search bar
            search_input = ".search-global-typeahead__input"
            await self.page.wait_for_selector(search_input, timeout=10000)
            await self.page.fill(search_input, search_query)
            await self.page.press(search_input, "Enter")
            
            # Wait for search results
            await self.page.wait_for_selector(".search-results-container", timeout=10000)
            
            self.logger.info("Search results loaded")
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    async def navigate_to_posts_filter(self):
        """Navigate to Posts filter"""
        try:
            self.logger.info("Looking for Posts filter")
            
            # Wait for filter buttons
            await self.page.wait_for_selector(".search-reusables__filter-list", timeout=10000)
            
            # Click Posts filter
            posts_filter = "button:has-text('Posts'), button[aria-label*='Posts']"
            await self.page.click(posts_filter)
            
            # Wait for posts to load
            await self.page.wait_for_selector(".feed-shared-update-v2", timeout=10000)
            
            self.logger.info("Successfully navigated to Posts filter")
            await asyncio.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to Posts filter: {e}")
            raise
    
    async def apply_date_filter_past_week(self):
        """Apply the 'Date posted' filter to 'Past week'"""
        try:
            self.logger.info("Applying 'Date posted' filter → Past week")

            # Look for date filter dropdown with multiple selectors
            date_filter_selectors = [
                "#searchFilter_datePosted",
                "button:has-text('Date posted')",
                "button[aria-label*='Date posted']",
                ".search-reusables__filter-list button:has-text('Date posted')"
            ]

            date_filter_found = False
            for selector in date_filter_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    await self.page.click(selector)
                    date_filter_found = True
                    break
                except:
                    continue

            if date_filter_found:
                await asyncio.sleep(1)

                # Select Past week option with multiple selectors
                past_week_selectors = [
                    "input#datePosted-past-week",
                    "label:has-text('Past week')",
                    "input[value='r604800']",
                    ".search-s-facet__form input[id*='past-week']"
                ]

                past_week_selected = False
                for selector in past_week_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=3000)
                        await self.page.click(selector)
                        past_week_selected = True
                        break
                    except:
                        continue

                if past_week_selected:
                    # Apply the filter
                    try:
                        show_results_btn = "button:has-text('Show results')"
                        await self.page.wait_for_selector(show_results_btn, timeout=5000)
                        await self.page.click(show_results_btn)
                        await asyncio.sleep(3)
                        self.logger.info("Successfully applied 'Past week' filter ✅")
                    except:
                        # Sometimes the filter is applied automatically
                        await asyncio.sleep(2)
                        self.logger.info("Date filter applied (auto-apply)")
                else:
                    self.logger.warning("Could not select Past week option")
            else:
                self.logger.warning("Could not find Date posted filter")

        except Exception as e:
            self.logger.warning(f"Failed to apply 'Date posted' filter: {e}")
            # Continue execution even if filter fails
            
        except Exception as e:
            self.logger.error(f"Failed to apply 'Date posted' filter: {e}")
            raise


    async def collect_post_links(self, target_count=50):
        """Collect post links by scrolling"""
        self.post_links = []
        scroll_attempts = 0
        max_scroll_attempts = 20000000000
        
        try:
            self.logger.info(f"Starting to collect {target_count} post links")
            
            while len(self.post_links) < target_count and scroll_attempts < max_scroll_attempts:
                # Get all post elements
                posts = await self.page.query_selector_all(".feed-shared-update-v2")
                
                for post in posts:
                    try:
                        # Look for post links
                        link_element = await post.query_selector("a[href*='/posts/'], a[href*='/feed/update/']")
                        if link_element:
                            post_url = await link_element.get_attribute('href')
                            
                            if post_url and post_url not in self.post_links:

                                if post_url.startswith("/"):
                                    post_url = f"https://www.linkedin.com{post_url}"
                                    
                                self.post_links.append(post_url)
                                self.logger.info(f"Collected post {len(self.post_links)}: {post_url}")
                                
                                if len(self.post_links) >= target_count:
                                    break
                                    
                    except Exception:
                        continue
                
                # Scroll down for more posts
                if len(self.post_links) < target_count:
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(2, 4))
                    scroll_attempts += 1
                    self.logger.info(f"Scrolled {scroll_attempts} times, collected {len(self.post_links)} posts")
            
            self.logger.info(f"Collection completed. Total posts collected: {len(self.post_links)}")
            
        except Exception as e:
            self.logger.error(f"Error collecting post links: {e}")
            raise
    
    async def save_to_csv(self, filename="linkedin_posts_playwright.csv"):
        """Save to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Post_URL'])
                for link in self.post_links:
                    writer.writerow([link])
            
            self.logger.info(f"Saved {len(self.post_links)} posts to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save CSV: {e}")
            raise
    
    async def save_to_json(self, filename="linkedin_posts_playwright.json"):
        """Save to JSON file"""
        try:
            data = {
                "total_posts": len(self.post_links),
                "collection_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "post_links": self.post_links
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.post_links)} posts to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            raise
    
    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        self.logger.info("Browser closed")
    
    async def run_scraping(self, hashtags, target_posts=50, save_format="both"):
        """Main scraping method"""
        try:
            await self.start_browser()
            await self.login_to_linkedin()
            await self.search_hashtags(hashtags)
            await self.navigate_to_posts_filter()
            await self.apply_date_filter_past_week()
            await self.collect_post_links(target_posts)
            
            # Save results
            if save_format in ["csv", "both"]:
                await self.save_to_csv()
            if save_format in ["json", "both"]:
                await self.save_to_json()
                
            return self.post_links
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            raise
        finally:
            await self.close_browser()

# Async usage example
async def main():
    INPUT = "aiml"
    HASHTAGS = [INPUT + " hiring"]
    TARGET_POSTS = 50
    
    scraper = LinkedInPostScraperPlaywright(EMAIL, PASSWORD, headless=False)
    
    try:
        collected_links = await scraper.run_scraping(
            hashtags=HASHTAGS,
            target_posts=TARGET_POSTS,
            save_format="both"
        )
        
        print(f"\nPlaywright scraping completed!")
        print(f"Total posts collected: {len(collected_links)}")
        print("Files saved: linkedin_posts_playwright.csv and linkedin_posts_playwright.json")
        
    except Exception as e:
        print(f"Scraping failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())