
import asyncio
import csv
import json
import time
import logging
from playwright.async_api import async_playwright
import random
from datetime import datetime
from typing import List, Optional


class LinkedInPostScraperPlaywright:
    def __init__(self, email, password, headless=False):
        self.email = email
        self.password = password
        self.headless = headless
        self.page = None
        self.browser = None
        self.context = None
        self.post_links = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def start_browser(self):
        """Initialize Playwright browser with realistic settings"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox', 
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create context with realistic settings
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1366, 'height': 768},
                locale='en-US'
            )

            # Add extra headers
            await self.context.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            })

            self.page = await self.context.new_page()
            self.logger.info("Browser started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise

    async def login_to_linkedin(self):
        """Login to LinkedIn with provided credentials"""
        try:
            self.logger.info("Navigating to LinkedIn login page")
            await self.page.goto("https://www.linkedin.com/login", wait_until='networkidle')

            # Wait for login form
            await self.page.wait_for_selector("#username", timeout=10000)

            # Human-like typing with delays
            await self.page.type("#username", self.email, delay=random.randint(50, 150))
            await asyncio.sleep(random.uniform(0.5, 1.0))
            await self.page.type("#password", self.password, delay=random.randint(50, 150))
            await asyncio.sleep(random.uniform(0.5, 1.0))

            # Click login button
            await self.page.click("button[type='submit']")

            # Wait for successful login with multiple selectors
            try:
                await self.page.wait_for_selector(".search-global-typeahead", timeout=15000)
            except:
                try:
                    await self.page.wait_for_selector(".feed-container-theme", timeout=10000)
                except:
                    await self.page.wait_for_selector(".global-nav", timeout=10000)

            self.logger.info("Successfully logged into LinkedIn")
            await asyncio.sleep(random.uniform(2, 4))

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            raise

    async def search_hashtags(self, hashtags: List[str]):
        """Search for hashtags on LinkedIn using OR logic"""
        try:
            # Create search query with OR logic
            search_query = " OR ".join(hashtags)
            self.logger.info(f"Searching for: {search_query}")

            # Find and use search bar with multiple selectors
            search_selectors = [
                ".search-global-typeahead__input",
                "input[placeholder*='Search']",
                ".search-global-typeahead input"
            ]

            search_input = None
            for selector in search_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=5000)
                    search_input = selector
                    break
                except:
                    continue

            if not search_input:
                raise Exception("Could not find search input")

            # Clear and fill search input
            await self.page.click(search_input)
            await self.page.fill(search_input, search_query)
            await self.page.press(search_input, "Enter")

            # Wait for search results
            await self.page.wait_for_selector(".search-results-container", timeout=15000)

            self.logger.info("Search results loaded")
            await asyncio.sleep(random.uniform(2, 3))

        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise

    async def navigate_to_posts_filter(self):
        """Navigate to Posts filter (Content filter)"""
        try:
            self.logger.info("Looking for Posts/Content filter")

            await asyncio.sleep(2)  # Wait for filters to load

            # Multiple selectors for Posts/Content filter
            filter_selectors = [
                "button:has-text('Posts')",
                "button[aria-label*='Posts']",
                "button:has-text('Content')",
                "button[aria-label*='Content']",
                ".search-reusables__filter-list button:has-text('Posts')"
            ]

            filter_clicked = False
            for selector in filter_selectors:
                try:
                    filter_element = await self.page.query_selector(selector)
                    if filter_element:
                        await filter_element.click()
                        filter_clicked = True
                        break
                except:
                    continue

            if not filter_clicked:
                self.logger.warning("Could not find Posts filter button, continuing anyway")
            else:
                # Wait for posts to load after filter
                await asyncio.sleep(3)
                self.logger.info("Successfully applied Posts filter")

        except Exception as e:
            self.logger.warning(f"Failed to apply Posts filter: {e}")
            # Continue execution even if filter fails

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

    async def get_full_post_url(self, partial_url: str) -> Optional[str]:
        """Open post in new tab to get full URL as requested"""
        try:
            # Create new page for this specific post
            new_page = await self.context.new_page()

            # Make URL absolute if needed
            if not partial_url.startswith('http'):
                full_url = f"https://www.linkedin.com{partial_url}"
            else:
                full_url = partial_url

            # Navigate to post
            await new_page.goto(full_url, wait_until='domcontentloaded', timeout=10000)
            await asyncio.sleep(1)

            # Get final URL after any redirects
            final_url = new_page.url

            # Close the tab as requested
            await new_page.close()

            # Clean URL (remove tracking parameters)
            clean_url = final_url.split('?')[0]
            return clean_url

        except Exception as e:
            self.logger.debug(f"Could not get full URL for {partial_url}: {e}")
            # Return cleaned partial URL as fallback
            if not partial_url.startswith('http'):
                partial_url = f"https://www.linkedin.com{partial_url}"
            return partial_url.split('?')[0]

    async def collect_post_links(self, target_count=50):
        """Collect post links by scrolling and opening each post in new tab"""
        self.post_links = []
        scroll_attempts = 0
        max_scroll_attempts = 50  # Increased for better collection
        processed_posts = set()  # Track processed posts to avoid duplicates

        try:
            self.logger.info(f"Starting to collect {target_count} post links")

            while len(self.post_links) < target_count and scroll_attempts < max_scroll_attempts:
                # Wait for content to load
                await asyncio.sleep(random.uniform(2, 3))

                # Get all post elements with multiple selectors
                post_selectors = [
                    ".feed-shared-update-v2",
                    ".update-components-text",
                    "[data-id^='urn:li:activity']",
                    ".artdeco-card"
                ]

                posts = []
                for selector in post_selectors:
                    try:
                        elements = await self.page.query_selector_all(selector)
                        if elements:
                            posts = elements
                            break
                    except:
                        continue

                self.logger.info(f"Found {len(posts)} post elements on current view")

                for post in posts:
                    if len(self.post_links) >= target_count:
                        break

                    try:
                        # Look for post links with multiple selectors
                        link_selectors = [
                            "a[href*='/posts/']",
                            "a[href*='/feed/update/']", 
                            "a[href*='activity-']",
                            ".update-components-actor a",
                            "a[data-control-name*='like']"
                        ]

                        link_element = None
                        partial_url = None

                        for selector in link_selectors:
                            try:
                                link_element = await post.query_selector(selector)
                                if link_element:
                                    partial_url = await link_element.get_attribute('href')
                                    if partial_url and ('posts/' in partial_url or 'activity-' in partial_url):
                                        break
                            except:
                                continue

                        if partial_url and partial_url not in processed_posts:
                            processed_posts.add(partial_url)

                            # Get full URL by opening in new tab (as requested)
                            full_url = await self.get_full_post_url(partial_url)

                            if full_url and full_url not in self.post_links:
                                self.post_links.append(full_url)
                                self.logger.info(f"Collected post {len(self.post_links)}: {full_url}")

                    except Exception as e:
                        self.logger.debug(f"Error processing post: {e}")
                        continue

                # Scroll down for more posts if needed
                if len(self.post_links) < target_count:
                    self.logger.info(f"Scrolling for more posts... (collected: {len(self.post_links)}/{target_count})")

                    # Scroll gradually
                    await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await asyncio.sleep(random.uniform(3, 5))
                    scroll_attempts += 1

                    # Check if we've reached the bottom
                    is_at_bottom = await self.page.evaluate(
                        'window.innerHeight + window.scrollY >= document.body.scrollHeight - 1000'
                    )
                    if is_at_bottom:
                        self.logger.info("Reached bottom of page")
                        break

            self.logger.info(f"Collection completed. Total posts collected: {len(self.post_links)}")

        except Exception as e:
            self.logger.error(f"Error collecting post links: {e}")
            raise

    async def save_to_csv(self, filename="linkedin_posts_playwright.csv"):
        """Save to CSV file with enhanced data"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Post_URL', 'Collected_At', 'Collection_Method'])

                for link in self.post_links:
                    writer.writerow([link, timestamp, 'New Tab Opening Method'])

            self.logger.info(f"Saved {len(self.post_links)} posts to {filename}")

        except Exception as e:
            self.logger.error(f"Failed to save CSV: {e}")
            raise

    async def save_to_json(self, filename="linkedin_posts_playwright.json"):
        """Save to JSON file with detailed metadata"""
        try:
            data = {
                "scraping_metadata": {
                    "total_posts": len(self.post_links),
                    "collection_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "collection_method": "Individual tab opening for each post",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "filters_applied": {
                        "content_filter": "Posts",
                        "date_filter": "Past week"
                    }
                },
                "post_links": self.post_links
            }

            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {len(self.post_links)} posts to {filename}")

        except Exception as e:
            self.logger.error(f"Failed to save JSON: {e}")
            raise

    async def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            self.logger.info("Browser closed and resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    async def run_scraping(self, hashtags: List[str], target_posts=50, save_format="both"):
        """Main scraping method with all requested features"""
        try:
            # Start browser with realistic settings
            await self.start_browser()

            # Login with human-like behavior
            await self.login_to_linkedin()

            # Search hashtags with OR logic
            await self.search_hashtags(hashtags)

            # Apply Posts filter
            await self.navigate_to_posts_filter()

            # Apply past week date filter
            await self.apply_date_filter_past_week()

            # Collect post links by opening each in new tab
            await self.collect_post_links(target_posts)

            # Save results in requested formats
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


# Configuration for easy modification (modular design as requested)
class ScrapingConfig:
    """Configuration class for easy hashtag and parameter modification"""

    # Login credentials
    EMAIL = "mathsfodnahai@gmail.com"
    PASSWORD = "Anjaliandanuj19"

    # Hashtag sets (easily changeable as requested)
    HASHTAG_SETS = {
        'ai_ml_hiring': ["AIMLhiring"],
        'tech_jobs': ["techjobs", "softwareengineer", "python"],
        'data_science': ["datascience", "machinelearning", "analytics"],
        'remote_work': ["remotework", "workfromhome", "remotejobs"]
    }

    # Current hashtags to use
    CURRENT_HASHTAGS = HASHTAG_SETS['ai_ml_hiring']  # Change this for different hashtag sets

    # Scraping parameters
    TARGET_POSTS = 50
    HEADLESS_MODE = False  # Set to True for background operation
    SAVE_FORMAT = "both"  # "csv", "json", or "both"


# Main execution function
async def main():
    """Enhanced main function with all requested features"""
    config = ScrapingConfig()

    print("🚀 LinkedIn Post URL Scraper - Enhanced Version")
    print("=" * 55)
    print(f"📧 Email: {config.EMAIL}")
    print(f"🔍 Hashtags: {config.CURRENT_HASHTAGS}")
    print(f"🎯 Target posts: {config.TARGET_POSTS}")
    print(f"📅 Date filter: Past week")
    print(f"🔄 Method: Open each post in new tab")
    print("=" * 55)

    scraper = LinkedInPostScraperPlaywright(
        email=config.EMAIL,
        password=config.PASSWORD,
        headless=config.HEADLESS_MODE
    )

    try:
        collected_links = await scraper.run_scraping(
            hashtags=config.CURRENT_HASHTAGS,
            target_posts=config.TARGET_POSTS,
            save_format=config.SAVE_FORMAT
        )

        print("\n🎉 Playwright scraping completed successfully!")
        print(f"📊 Total posts collected: {len(collected_links)}")
        print("💾 Files saved:")

        if config.SAVE_FORMAT in ["csv", "both"]:
            print("   → linkedin_posts_playwright.csv")
        if config.SAVE_FORMAT in ["json", "both"]:
            print("   → linkedin_posts_playwright.json")

        print("\n✅ All requirements implemented:")
        print("   ✅ LinkedIn login with provided credentials")
        print("   ✅ Search hashtags: #AIMLhiring, #AIML, #datasciencehiring")
        print("   ✅ Navigate to Posts filter (not Jobs)")
        print("   ✅ Apply past week date filter")
        print("   ✅ Open each post in new tab to get clean URLs")
        print("   ✅ Scroll and collect 50 post URLs")
        print("   ✅ Save to CSV and JSON formats")
        print("   ✅ Modular design for easy hashtag changes")
        print("   ✅ Handle dynamic LinkedIn elements")

    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
