"""
Web search functionality for AREN
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import random
from datetime import datetime
from utils.logging_utils import logger

def web_search(query):
    """
    Web search function using DuckDuckGo
    """
    # Check if this is an identity question that was mistakenly routed here
    if is_identity_question(query):
        logger.warning(f"Identity question detected in search: {query}")
        return "I am A.R.E.N., your AI assistant. I can help you with various tasks. Ask me about the time, date, search for information, or open applications!"
    
    # Check for predefined search results first
    predefined_result = get_predefined_search_result(query)
    if predefined_result:
        logger.info(f"Using predefined result for query: {query}")
        return predefined_result
        
    # Pre-process the query for better results
    logger.info(f"Processing search query: {query}")
    processed_query = preprocess_query(query)
    
    # Format the search query for URL
    encoded_query = urllib.parse.quote(processed_query)
    
    # User-Agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    
    try:
        # Use DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = []
            for result in soup.find_all('div', {'class': 'result'}):
                title_elem = result.find('a', {'class': 'result__a'})
                snippet_elem = result.find('a', {'class': 'result__snippet'})
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    snippet = snippet_elem.get_text().strip()
                    if title and snippet:
                        results.append({
                            'title': title,
                            'snippet': snippet
                        })
            
            # If we found results, format them into a response
            if results:
                # For queries about people, try to find biographical information
                if query.lower().startswith(('who is', 'who was', 'what is', 'what was')):
                    for result in results:
                        # Look for biographical snippets
                        if any(word in result['snippet'].lower() for word in ['born', 'is a', 'was a', 'known for', 'famous']):
                            return result['snippet']
                
                # For other queries, combine relevant information
                relevant_snippets = [result['snippet'] for result in results[:2]]
                combined_response = ' '.join(relevant_snippets)
                
                # Clean up the response
                combined_response = re.sub(r'\s+', ' ', combined_response)  # Remove extra whitespace
                combined_response = combined_response.replace('...', '.')    # Clean up ellipsis
                
                return combined_response
        
        # If no results found or error occurred, try alternative search
        alternative_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
        alt_response = requests.get(alternative_url, headers=headers, timeout=10)
        
        if alt_response.status_code == 200:
            data = alt_response.json()
            if data.get('Abstract'):
                return data['Abstract']
            elif data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                return data['RelatedTopics'][0].get('Text', '')
        
        # If all else fails, provide a fallback response
        return get_fallback_response(query)
        
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return f"I couldn't complete the search right now. You could try asking again with different wording."

def preprocess_query(query):
    """
    Preprocess and improve search queries
    """
    query_lower = query.lower()
    
    # Handle common grammar issues
    if "who build" in query_lower:
        query = query.replace("who build", "who built")
    elif "who create" in query_lower:
        query = query.replace("who create", "who created")
    
    # Handle specific landmarks/topics with specialized queries
    if "taj mahal" in query_lower:
        if any(term in query_lower for term in ["build", "built", "create", "created", "construct", "constructed"]):
            query = "Taj Mahal builder Shah Jahan history"
            
    # Remove common filler words for better search results
    filler_words = ["please", "can you", "could you", "tell me", "i want to know", "search for", "find", "look up"]
    for word in filler_words:
        if word in query_lower:
            query = query.replace(word, "").strip()
    
    return query

def search_taj_mahal(query):
    """
    Specialized function for Taj Mahal questions since it's a common query
    """
    # Hard-coded responses for common Taj Mahal questions
    if any(term in query.lower() for term in ["built", "build", "create", "created", "construct", "constructed", "made"]):
        return "The Taj Mahal was built by Mughal Emperor Shah Jahan in memory of his wife Mumtaz Mahal. Construction began around 1632 and was completed in 1653. The project employed thousands of artisans and craftsmen under the guidance of the architect Ustad Ahmad Lahauri."
    
    # General Taj Mahal information
    return "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in Agra, India. It was commissioned in 1631 by the Mughal emperor Shah Jahan to house the tomb of his favorite wife, Mumtaz Mahal. The tomb is the centerpiece of a 17-hectare complex, which includes a mosque and a guest house, and is set in formal gardens bounded on three sides by a crenellated wall."

def is_identity_question(query):
    """
    Check if the query is asking about AREN's identity
    This is a backup in case such queries get routed to search
    """
    identity_keywords = [
        "who are you", "your name", "what are you",
        "tell me about you", "tell me about yourself",
        "what is your name", "what's your name",
        "tum kaun ho", "aap kaun ho", "tumhara naam kya hai"
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in identity_keywords)

def get_predefined_search_result(query):
    """
    Return predefined answers for common search queries
    
    Args:
        query (str): The search query
        
    Returns:
        str or None: A predefined answer or None if there's no match
    """
    query_lower = query.lower()
    
    # Common predefined searches
    predefined_searches = {
        "when was python created": "Python was created by Guido van Rossum and first released in 1991. It was developed as a successor to the ABC language and named after the British comedy group Monty Python.",
        
        "who invented the internet": "The Internet was not invented by a single person. It evolved from the ARPANET, which was developed in the late 1960s by the Advanced Research Projects Agency (ARPA) of the U.S. Department of Defense. Key contributors include Vint Cerf and Bob Kahn who developed TCP/IP in the 1970s, which became the standard networking protocol of the Internet.",
        
        "tallest mountain in the world": "Mount Everest is the tallest mountain above sea level, with a height of 8,848.86 meters (29,031.7 feet). However, if measured from base to peak, Mauna Kea in Hawaii is taller at 10,211 meters (33,500 feet), with much of it underwater.",
        
        "latest news": get_simulated_news(),
        
        "fastest animal": "The peregrine falcon is considered the fastest animal, capable of reaching speeds over 389 km/h (242 mph) during its hunting dive (stoop). On land, the cheetah is the fastest animal, reaching speeds up to 120 km/h (75 mph) in short bursts.",
        
        "deepest ocean": "The Mariana Trench in the western Pacific Ocean is the deepest known part of the Earth's oceans, with a maximum depth of approximately 10,994 meters (36,070 feet) at a location called Challenger Deep.",
        
        "largest country": "Russia is the largest country in the world by land area, covering approximately 17,098,246 square kilometers (6,601,670 square miles), spanning Eastern Europe and Northern Asia.",
        
        "most populated country": "As of 2023, India surpassed China to become the most populated country in the world with approximately 1.43 billion people, while China has about 1.426 billion people.",
        
        "how many planets in solar system": "There are eight recognized planets in our solar system: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Pluto was reclassified as a 'dwarf planet' by the International Astronomical Union in 2006."
    }
    
    # Check for exact matches
    if query_lower in predefined_searches:
        return predefined_searches[query_lower]
    
    # Check for partial matches
    for key, value in predefined_searches.items():
        if key in query_lower or all(word in query_lower for word in key.split()):
            return value
    
    return None

def get_simulated_news():
    """
    Generate simulated news headlines when the user asks for news
    
    Returns:
        str: Simulated news headlines
    """
    today = datetime.now().strftime("%B %d, %Y")
    
    news_headlines = [
        "Scientists Report Breakthrough in Renewable Energy Storage Technology",
        "New AI Model Shows Promise in Early Disease Detection",
        "Global Summit on Climate Change Concludes with New Agreements",
        "Major Tech Companies Announce Collaboration on Cybersecurity",
        "Researchers Discover New Species in Amazon Rainforest",
        "International Space Station Celebrates 25 Years in Orbit",
        "Global Economy Shows Signs of Recovery, According to Latest Report",
        "New Educational Program Aims to Bridge Digital Divide",
        "Sports Update: Championship Finals Set to Begin This Weekend",
        "Cultural Heritage Preservation Efforts Gain International Support"
    ]
    
    # Select a few random headlines
    selected_headlines = random.sample(news_headlines, 5)
    
    # Format the news response
    news_response = f"Latest News Headlines ({today}):\n\n"
    for i, headline in enumerate(selected_headlines, 1):
        news_response += f"{i}. {headline}\n"
    
    news_response += "\nNote: These are simulated headlines for demonstration purposes."
    
    return news_response

def get_fallback_response(query):
    """
    Provide helpful fallback responses when search fails
    
    Args:
        query (str): The original query
        
    Returns:
        str: A helpful fallback response
    """
    fallback_responses = [
        f"I searched for information about '{query}' but couldn't find specific details. Try rephrasing your question or being more specific.",
        f"I don't have enough information about '{query}' at the moment. Could you provide more details or ask in a different way?",
        f"I'm not able to find reliable information about '{query}' right now. You might want to try a more specific question.",
        f"I don't have complete information about '{query}' in my knowledge base. Try asking about a related but more general topic."
    ]
    
    return random.choice(fallback_responses) 