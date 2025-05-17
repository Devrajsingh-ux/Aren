import yfinance as yf
from nsepy import get_history
from datetime import date, timedelta
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class StockMarketFeature:
    def __init__(self):
        self.nse_symbols = {
            'NIFTY': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            'RELIANCE': 'RELIANCE.NS',
            'TCS': 'TCS.NS',
            'HDFCBANK': 'HDFCBANK.NS',
            'INFY': 'INFY.NS',
            'ICICIBANK': 'ICICIBANK.NS',
            'HINDUNILVR': 'HINDUNILVR.NS',
            'SBIN': 'SBIN.NS',
            'BHARTIARTL': 'BHARTIARTL.NS'
        }

    def can_handle(self, text: str) -> bool:
        """Check if the input text is related to stock market."""
        stock_keywords = ['stock', 'share', 'market', 'nifty', 'sensex', 'price', 'trading']
        return any(keyword in text.lower() for keyword in stock_keywords)

    def process(self, text: str) -> str:
        """Process stock market related queries."""
        try:
            text = text.lower()
            
            # Market summary
            if any(phrase in text for phrase in ['market summary', 'market status', 'market update']):
                return self._get_market_summary_text()
            
            # Stock price
            if 'price' in text:
                for symbol in self.nse_symbols:
                    if symbol.lower() in text:
                        return self._get_stock_info_text(symbol)
            
            # Top gainers and losers
            if any(phrase in text for phrase in ['top gainers', 'top losers', 'gainers', 'losers']):
                return self._get_gainers_losers_text()
            
            # Historical data
            if any(phrase in text for phrase in ['history', 'historical', 'past']):
                for symbol in self.nse_symbols:
                    if symbol.lower() in text:
                        return self._get_historical_data_text(symbol)
            
            # Default response
            return "I can help you with stock market information. You can ask me about:\n" + \
                   "- Market summary\n" + \
                   "- Stock prices (e.g., 'What is the price of RELIANCE?')\n" + \
                   "- Top gainers and losers\n" + \
                   "- Historical data (e.g., 'Show me RELIANCE history')"
                   
        except Exception as e:
            logger.error(f"Error processing stock market query: {str(e)}")
            return "Sorry, I encountered an error while processing your stock market query."

    def get_stock_info(self, symbol: str) -> Dict:
        """Get basic information about a stock."""
        try:
            if symbol in self.nse_symbols:
                stock = yf.Ticker(self.nse_symbols[symbol])
                info = stock.info
                return {
                    'symbol': symbol,
                    'name': info.get('longName', 'N/A'),
                    'current_price': info.get('currentPrice', 'N/A'),
                    'previous_close': info.get('previousClose', 'N/A'),
                    'day_high': info.get('dayHigh', 'N/A'),
                    'day_low': info.get('dayLow', 'N/A'),
                    'volume': info.get('volume', 'N/A'),
                    'market_cap': info.get('marketCap', 'N/A')
                }
            else:
                return {'error': f'Symbol {symbol} not found in database'}
        except Exception as e:
            logger.error(f"Error getting stock info: {str(e)}")
            return {'error': f'Error fetching data: {str(e)}'}

    def _get_market_summary_text(self) -> str:
        """Get formatted market summary text."""
        try:
            summary = {}
            for symbol in ['NIFTY', 'BANKNIFTY']:
                stock = yf.Ticker(self.nse_symbols[symbol])
                info = stock.info
                summary[symbol] = {
                    'current': info.get('currentPrice', 'N/A'),
                    'change': info.get('regularMarketChange', 'N/A'),
                    'change_percent': info.get('regularMarketChangePercent', 'N/A')
                }
            
            response = "Market Summary:\n"
            for symbol, data in summary.items():
                response += f"\n{symbol}:\n"
                response += f"Current: {data['current']}\n"
                response += f"Change: {data['change']} ({data['change_percent']}%)"
            
            return response
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return "Sorry, I couldn't fetch the market summary."

    def _get_stock_info_text(self, symbol: str) -> str:
        """Get formatted stock information text."""
        try:
            if symbol in self.nse_symbols:
                stock = yf.Ticker(self.nse_symbols[symbol])
                info = stock.info
                response = f"\n{symbol} Stock Information:\n"
                response += f"Current Price: {info.get('currentPrice', 'N/A')}\n"
                response += f"Previous Close: {info.get('previousClose', 'N/A')}\n"
                response += f"Day High: {info.get('dayHigh', 'N/A')}\n"
                response += f"Day Low: {info.get('dayLow', 'N/A')}\n"
                response += f"Volume: {info.get('volume', 'N/A')}\n"
                response += f"Market Cap: {info.get('marketCap', 'N/A')}"
                return response
            else:
                return f"Sorry, I don't have information for {symbol}."
        except Exception as e:
            logger.error(f"Error getting stock info: {str(e)}")
            return f"Sorry, I couldn't fetch information for {symbol}."

    def get_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for a stock."""
        try:
            if symbol in self.nse_symbols:
                end_date = date.today()
                start_date = end_date - timedelta(days=days)
                return get_history(symbol=symbol,
                                 start=start_date,
                                 end=end_date)
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()

    def _get_historical_data_text(self, symbol: str) -> str:
        """Get formatted historical data text."""
        try:
            if symbol in self.nse_symbols:
                data = self.get_historical_data(symbol, days=7)
                if isinstance(data, pd.DataFrame) and not data.empty:
                    response = f"\n{symbol} Historical Data (Last 7 days):\n"
                    for index, row in data.iterrows():
                        response += f"\n{index.strftime('%Y-%m-%d')}:\n"
                        response += f"Open: {row['Open']}\n"
                        response += f"High: {row['High']}\n"
                        response += f"Low: {row['Low']}\n"
                        response += f"Close: {row['Close']}\n"
                        response += f"Volume: {row['Volume']}"
                    return response
                else:
                    return f"Sorry, I couldn't fetch historical data for {symbol}."
            else:
                return f"Sorry, I don't have historical data for {symbol}."
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return f"Sorry, I couldn't fetch historical data for {symbol}."

    def _get_gainers_losers_text(self) -> str:
        """Get formatted top gainers and losers text."""
        try:
            gainers, losers = self._get_top_gainers_losers()
            
            response = "Top Gainers:\n"
            for stock in gainers:
                response += f"\n{stock['symbol']} ({stock['name']}):\n"
                response += f"Price: {stock['price']}\n"
                response += f"Change: {stock['change_percent']}%"
            
            response += "\n\nTop Losers:\n"
            for stock in losers:
                response += f"\n{stock['symbol']} ({stock['name']}):\n"
                response += f"Price: {stock['price']}\n"
                response += f"Change: {stock['change_percent']}%"
            
            return response
        except Exception as e:
            logger.error(f"Error getting gainers/losers: {str(e)}")
            return "Sorry, I couldn't fetch the top gainers and losers."

    def _get_top_gainers_losers(self) -> Tuple[List[Dict], List[Dict]]:
        """Get top gainers and losers of the day."""
        try:
            gainers = []
            losers = []
            for symbol in self.nse_symbols:
                if symbol not in ['NIFTY', 'BANKNIFTY']:
                    stock = yf.Ticker(self.nse_symbols[symbol])
                    info = stock.info
                    change = info.get('regularMarketChangePercent', 0)
                    stock_info = {
                        'symbol': symbol,
                        'name': info.get('longName', 'N/A'),
                        'price': info.get('currentPrice', 'N/A'),
                        'change_percent': change
                    }
                    if change > 0:
                        gainers.append(stock_info)
                    else:
                        losers.append(stock_info)
            
            gainers.sort(key=lambda x: x['change_percent'], reverse=True)
            losers.sort(key=lambda x: x['change_percent'])
            
            return gainers[:5], losers[:5]
        except Exception as e:
            logger.error(f"Error getting gainers/losers: {str(e)}")
            return [], []

def main():
    # Example usage
    market = StockMarketFeature()
    
    # Get market summary
    summary = market.process("market summary")
    print("\nMarket Summary:")
    print(summary)
    
    # Get stock info
    stock_info = market.process("What is the price of RELIANCE?")
    print("\nStock Info for RELIANCE:")
    print(stock_info)
    
    # Get historical data
    hist_data = market.process("Show me RELIANCE history")
    print("\nHistorical Data for RELIANCE:")
    print(hist_data)
    
    # Get top gainers and losers
    gainers_losers = market.process("top gainers")
    print("\nTop Gainers and Losers:")
    print(gainers_losers)

if __name__ == "__main__":
    main() 