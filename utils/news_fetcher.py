import requests
import feedparser
import streamlit as st
from datetime import datetime, timedelta
import trafilatura
import re
from urllib.parse import quote

class NewsFetcher:
    """Class to fetch relevant stock news"""
    
    def __init__(self):
        self.news_sources = {
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'reuters_business': 'https://feeds.reuters.com/reuters/businessNews',
            'google_news': 'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
        }
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_stock_news(_self, symbol, company_name=None, max_articles=5):
        """
        Fetch news related to a specific stock
        
        Args:
            symbol (str): Stock symbol
            company_name (str): Company name for better search results
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of news articles
        """
        articles = []
        
        # Create search queries
        queries = [symbol]
        if company_name:
            # Clean company name for search
            clean_name = re.sub(r'\b(Inc|Corp|Ltd|Limited|Company|Co)\b\.?', '', company_name, flags=re.IGNORECASE)
            clean_name = clean_name.strip()
            if clean_name:
                queries.append(clean_name)
        
        for query in queries:
            try:
                # Get Google News RSS feed
                google_news_url = _self.news_sources['google_news'].format(query=quote(query))
                google_articles = _self._fetch_rss_feed(google_news_url, max_items=3)
                articles.extend(google_articles)
                
                if len(articles) >= max_articles:
                    break
                    
            except Exception as e:
                st.warning(f"Could not fetch news from Google News: {e}")
                continue
        
        # Try Yahoo Finance RSS as backup
        try:
            yahoo_articles = _self._fetch_rss_feed(_self.news_sources['yahoo_finance'], max_items=2)
            articles.extend(yahoo_articles)
        except Exception as e:
            st.warning(f"Could not fetch news from Yahoo Finance: {e}")
        
        # Remove duplicates and limit results
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            if article['title'] not in seen_titles and len(unique_articles) < max_articles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        return unique_articles
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_market_news(_self, max_articles=8):
        """
        Fetch general market news
        
        Args:
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of market news articles
        """
        articles = []
        
        # Fetch from multiple sources
        sources = [
            ('Yahoo Finance', _self.news_sources['yahoo_finance']),
            ('MarketWatch', _self.news_sources['marketwatch']),
            ('Reuters Business', _self.news_sources['reuters_business'])
        ]
        
        for source_name, url in sources:
            try:
                source_articles = _self._fetch_rss_feed(url, max_items=3)
                for article in source_articles:
                    article['source'] = source_name
                articles.extend(source_articles)
                
            except Exception as e:
                st.warning(f"Could not fetch news from {source_name}: {e}")
                continue
        
        # Remove duplicates and limit results
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            if article['title'] not in seen_titles and len(unique_articles) < max_articles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        return unique_articles
    
    def _fetch_rss_feed(self, url, max_items=5):
        """
        Fetch and parse RSS feed
        
        Args:
            url (str): RSS feed URL
            max_items (int): Maximum items to return
            
        Returns:
            list: List of articles
        """
        try:
            # Parse RSS feed
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries[:max_items]:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    
                    # Get article summary
                    summary = ""
                    if hasattr(entry, 'summary'):
                        # Clean HTML tags from summary
                        summary = re.sub(r'<[^>]+>', '', entry.summary)
                        summary = summary.strip()[:200] + "..." if len(summary) > 200 else summary
                    
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'No Title',
                        'link': entry.link if hasattr(entry, 'link') else '',
                        'summary': summary,
                        'published': pub_date.strftime('%Y-%m-%d %H:%M') if pub_date else 'Unknown',
                        'source': feed.feed.title if hasattr(feed.feed, 'title') else 'Unknown'
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            st.warning(f"Error fetching RSS feed {url}: {e}")
            return []
    
    def get_hk_market_news(self, max_articles=5):
        """
        Fetch Hong Kong market specific news
        
        Args:
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of HK market news articles
        """
        hk_queries = [
            "Hong Kong stock market",
            "HKEX",
            "Hang Seng Index",
            "HSI"
        ]
        
        articles = []
        
        for query in hk_queries:
            try:
                google_news_url = self.news_sources['google_news'].format(query=quote(query))
                query_articles = self._fetch_rss_feed(google_news_url, max_items=2)
                articles.extend(query_articles)
                
                if len(articles) >= max_articles:
                    break
                    
            except Exception as e:
                continue
        
        # Remove duplicates
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            if article['title'] not in seen_titles and len(unique_articles) < max_articles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        return unique_articles
    
    def format_time_ago(self, published_str):
        """
        Format published time as 'time ago'
        
        Args:
            published_str (str): Published time string
            
        Returns:
            str: Formatted time ago string
        """
        try:
            if published_str == 'Unknown':
                return 'Unknown'
            
            pub_date = datetime.strptime(published_str, '%Y-%m-%d %H:%M')
            now = datetime.now()
            diff = now - pub_date
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
                
        except Exception:
            return published_str