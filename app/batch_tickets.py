import requests
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import dotenv
import argparse
import json

dotenv.load_dotenv()

api_key = os.getenv("FRESHDESK_API_KEY")
domain = os.getenv("FRESHDESK_DOMAIN")

class FreshdeskBatchFetcher:
    def __init__(self, api_key: str = api_key, domain: str = domain):
        self.api_key = api_key
        self.domain = domain
        self.auth = (api_key, 'X')
        self.base_url = f"https://{domain}/api/v2"
        
        # Rate limiting parameters
        self.last_fetch_time = None
        self.min_fetch_interval = timedelta(minutes=5)  # Minimum time between fetches
        self.tickets_cache = []
        self.last_fetch_count = 0
        self.total_fetches = 0

    def _can_fetch(self) -> bool:
        """Check if enough time has passed since the last fetch"""
        if not self.last_fetch_time:
            return True
        return datetime.now() - self.last_fetch_time >= self.min_fetch_interval

    def _make_request(self, url: str) -> Optional[Dict]:
        """Make an API request with error handling"""
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {str(e)}")
            return None

    def fetch_ticket_batch(self, page: int = 1, per_page: int = 100, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch a batch of tickets with pagination and optional limit
        Args:
            page: Page number to fetch
            per_page: Number of tickets per page
            limit: Maximum total number of tickets to return
        """
        # if not self._can_fetch():
        #     time_to_wait = (self.last_fetch_time + self.min_fetch_interval - datetime.now()).seconds
        #     print(f"Rate limit: Please wait {time_to_wait} seconds before fetching again")
        #     return self.tickets_cache

        # Adjust per_page if limit is smaller
        if limit:
            per_page = min(per_page, limit)
            page = max(1, limit // per_page)

        url = f"{self.base_url}/tickets?page={page}&per_page={per_page}&include=description"
        tickets = self._make_request(url)
                
        if tickets:
            self.last_fetch_time = datetime.now()
            # Apply limit if specified
            if limit:
                tickets = tickets[:limit]
            self.last_fetch_count = len(tickets)
            self.total_fetches += 1
            self.tickets_cache = tickets
            return tickets
        return []

    # Utility methods
    def get_last_fetch_count(self) -> int:
        """Return the number of tickets from the last fetch"""
        return self.last_fetch_count

    def get_total_fetches(self) -> int:
        """Return the total number of fetch operations performed"""
        return self.total_fetches

    def get_time_since_last_fetch(self) -> Optional[timedelta]:
        """Return time elapsed since last fetch"""
        if self.last_fetch_time:
            return datetime.now() - self.last_fetch_time
        return None

    def get_cache_size(self) -> int:
        """Return the number of tickets in cache"""
        return len(self.tickets_cache)

# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Fetch Freshdesk tickets'
    )
    parser.add_argument(
        '--limit', 
        type=int, 
        default=5,
        help='Number of tickets to fetch details for (default: 5)'
    )
    args = parser.parse_args()
    limit = args.limit if args.limit else 5
    
    fetcher = FreshdeskBatchFetcher(api_key, domain)
    
    # Fetch batch of tickets
    tickets = fetcher.fetch_ticket_batch(page=1, per_page=100, limit=limit)
    print(f"Fetched {fetcher.get_last_fetch_count()} tickets")
    
    # Utility method examples
    print(f"Total fetch operations: {fetcher.get_total_fetches()}")
    print(f"Cache size: {fetcher.get_cache_size()}")
    if fetcher.get_time_since_last_fetch():
        print(f"Time since last fetch: {fetcher.get_time_since_last_fetch().seconds} seconds")
        
    print(json.dumps(tickets, indent=4))
