
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class WebScraping:
    def __init__(self) -> None:
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Set up the Chrome WebDriver with options."""
        options = Options()
        options.add_argument('--headless')  # Run headless Chrome for efficiency
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def access_url(self, url: str):
        """Access a specified URL."""
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Error accessing {url}: {e}")
            return ModuleNotFoundError

    def get_page_title(self) -> str:
        """Get the title of the current page."""
        return self.driver.title

    def get_text_by_xpath(self, xpath: str) -> str:
        """Get text content of an element identified by XPath."""
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
            element = self.driver.find_element_by_xpath(xpath)
            return element.text
        except Exception as e:
            print(f"Error finding element by XPath {xpath}: {e}")
            return ""

    def get_elements_by_class_name(self, class_name: str):
        """Get elements identified by class name."""
        try:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            elements = self.driver.find_elements_by_class_name(class_name)
            return elements
        except Exception as e:
            print(f"Error finding elements by class name {class_name}: {e}")
            return []

    def click_element_by_xpath(self, xpath: str):
        """Click an element identified by XPath."""
        try:
            element = self.driver.find_element_by_xpath(xpath)
            element.click()
        except Exception as e:
            print(f"Error clicking element by XPath {xpath}: {e}")

    def input_text_by_xpath(self, xpath: str, text: str):
        """Input text into an element identified by XPath."""
        try:
            element = self.driver.find_element_by_xpath(xpath)
            element.clear()
            element.send_keys(text)
        except Exception as e:
            print(f"Error inputting text by XPath {xpath}: {e}")

    def close_driver(self):
        """Close the WebDriver."""
        self.driver.quit()

# Example usage
if __name__ == "__main__":
    scraper = WebScraping()
    scraper.access_url("https://www.example.com")
    print(scraper.get_page_title())
    print(scraper.get_text_by_xpath("//h1"))
    scraper.close_driver()
