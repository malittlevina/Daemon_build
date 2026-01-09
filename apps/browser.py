from core.module import Module
import requests
from bs4 import BeautifulSoup
import urllib.parse

class Browser(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.history = []
        self.current_url = None
        self.bookmarks = []
        self.page_content = ""

    def initialize(self):
        self.kernel.log("Browser", "Initialized.")

    def start(self):
        pass

    def stop(self):
        pass

    def navigate(self, url):
        """Navigate to a URL and fetch text content."""
        if not url.startswith("http"):
            url = "https://" + url
            
        self.kernel.log("Browser", f"Navigating to: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Update State
            if self.current_url:
                self.history.append(self.current_url)
            self.current_url = url
            
            # Parse Content
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract title and text
            title = soup.title.string if soup.title else url
            paragraphs = soup.find_all("p")
            text_content = "\n".join(p.get_text() for p in paragraphs if p.get_text())
            
            self.page_content = text_content[:2000] # Limit buffer
            
            summary = f"Title: {title}\nLength: {len(text_content)} chars"
            self.kernel.log("Browser", f"Loaded page. {summary}")
            return f"Loaded: {title}\n\n{text_content[:500]}..."
            
        except Exception as e:
            self.kernel.log("Browser", f"Navigation failed: {e}", level="error")
            return f"Error loading {url}: {e}"

    def search(self, query):
        """Perform a search (DuckDuckGo Lite)"""
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
        return self.navigate(url)

    def back(self):
        if self.history:
            url = self.history.pop()
            return self.navigate(url)
        return "History empty."

    def get_content(self):
        return self.page_content
