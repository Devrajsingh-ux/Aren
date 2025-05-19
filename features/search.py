import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

def web_search(query):
    """
    Web search function that directly scrapes search results
    No API keys are used - only direct web scraping
    """
    # Format the search query for URL
    encoded_query = urllib.parse.quote(query)
    
    # User-Agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    
    try:
        # First try to get information from Wikipedia snippets via search
        search_url = f"https://en.wikipedia.org/w/index.php?search={encoded_query}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if this is a direct article page
            main_content = soup.find('div', {'class': 'mw-parser-output'})
            if main_content:
                # Try to extract the first few paragraphs
                paragraphs = main_content.find_all('p')
                for p in paragraphs[:3]:  # Look at first 3 paragraphs
                    text = p.get_text().strip()
                    if len(text) > 100:  # Only consider substantial paragraphs
                        # Clean up the text (remove citations, etc.)
                        text = re.sub(r'\[\d+\]', '', text)
                        return text
            
            # If not a direct hit, check search results
            search_results = soup.find('ul', {'class': 'mw-search-results'})
            if search_results:
                # Found search results, try to follow the first link
                first_result = search_results.find('a')
                if first_result and 'href' in first_result.attrs:
                    article_url = f"https://en.wikipedia.org{first_result['href']}"
                    article_response = requests.get(article_url, headers=headers, timeout=10)
                    
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.text, 'html.parser')
                        article_content = article_soup.find('div', {'class': 'mw-parser-output'})
                        
                        if article_content:
                            paragraphs = article_content.find_all('p')
                            for p in paragraphs[:3]:
                                text = p.get_text().strip()
                                if len(text) > 100:
                                    text = re.sub(r'\[\d+\]', '', text)
                                    return text
        
        # Fallback to a general search approach if Wikipedia doesn't yield results
        # Try an alternative search (simulating a more general search)
        # This is a simplified approach without using specific search engine APIs
        
        # Try with a different query format if specific patterns are detected
        if query.lower().startswith("who build "):
            return web_search(query.lower().replace("who build ", "who built "))
        elif query.lower().startswith("who create "):
            return web_search(query.lower().replace("who create ", "who created "))
        
        # If all else fails, provide a general response
        return f"I searched for information about '{query}' but couldn't find specific details. Try rephrasing your question or being more specific."
        
    except Exception as e:
        return f"Web search encountered an error: {str(e)}. Please try again with a different query."
