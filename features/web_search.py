import requests
from bs4 import BeautifulSoup
import webbrowser
import logging
from typing import Tuple, Optional
import re
from urllib.parse import quote_plus
import time

logger = logging.getLogger(__name__)

class WebSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_and_summarize(self, query: str) -> Tuple[str, str]:
        """
        Search for information and return both summary and URL.
        Returns: (summary, url)
        """
        try:
            # Format the search query
            search_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={search_query}"
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            # Fetch the search results
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse the results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors for search results
            search_results = (
                soup.find_all('div', class_='g') or
                soup.find_all('div', class_='yuRUbf') or
                soup.find_all('div', {'data-hveid': True})
            )
            
            if not search_results:
                # If no results found, try DuckDuckGo as fallback
                return self._search_duckduckgo(query)
            
            # Get the first result
            first_result = search_results[0]
            
            # Extract title and snippet
            title_element = (
                first_result.find('h3') or
                first_result.find('div', class_='vvjwJb') or
                first_result.find('a', class_='BVG0Nb')
            )
            
            snippet_element = (
                first_result.find('div', class_='VwiC3b') or
                first_result.find('div', class_='st') or
                first_result.find('span', class_='aCOpRe')
            )
            
            title = title_element.text if title_element else "No title found"
            snippet = snippet_element.text if snippet_element else "No description available"
            
            # Extract the URL
            link_element = first_result.find('a')
            url = link_element['href'] if link_element and 'href' in link_element.attrs else search_url
            
            # Create summary
            summary = f"Title: {title}\n\nSummary: {snippet}\n\nWould you like me to open the full page?"
            
            return summary, url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during web search: {str(e)}")
            return "Sorry, I encountered a network error while searching. Please check your internet connection.", ""
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return "Sorry, I encountered an error while searching.", ""

    def _search_duckduckgo(self, query: str) -> Tuple[str, str]:
        """Fallback search using DuckDuckGo."""
        try:
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result = soup.find('div', class_='result')
            
            if result:
                title = result.find('h2').text if result.find('h2') else "No title found"
                snippet = result.find('a', class_='result__snippet').text if result.find('a', class_='result__snippet') else "No description available"
                url = result.find('a', class_='result__url')['href'] if result.find('a', class_='result__url') else search_url
                
                summary = f"Title: {title}\n\nSummary: {snippet}\n\nWould you like me to open the full page?"
                return summary, url
            
            return "No results found.", ""
            
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}")
            return "Sorry, I encountered an error while searching.", ""

    def open_webpage(self, url: str) -> bool:
        """Open a webpage in the default browser."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"Error opening webpage: {str(e)}")
            return False

    def get_wikipedia_summary(self, query: str) -> Optional[str]:
        """Get a summary from Wikipedia."""
        try:
            # Format the search query for Wikipedia
            search_query = quote_plus(query)
            search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={search_query}"
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            # Fetch the search results
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Parse the results
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first result
            first_result = soup.find('div', class_='mw-search-result-heading')
            if not first_result:
                return None
            
            # Get the article URL
            article_url = "https://en.wikipedia.org" + first_result.find('a')['href']
            
            # Fetch the article
            article_response = self.session.get(article_url, timeout=10)
            article_response.raise_for_status()
            
            # Parse the article
            article_soup = BeautifulSoup(article_response.text, 'html.parser')
            
            # Get the first paragraph
            first_paragraph = article_soup.find('div', class_='mw-parser-output').find('p', recursive=False)
            if not first_paragraph:
                return None
            
            # Clean the text
            summary = first_paragraph.text.strip()
            summary = re.sub(r'\[\d+\]', '', summary)  # Remove reference numbers
            
            return summary
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting Wikipedia summary: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting Wikipedia summary: {str(e)}")
            return None 