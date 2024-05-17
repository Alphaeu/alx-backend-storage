import requests
import redis
from functools import wraps
import time

# Initialize Redis client
cache = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_page(func):
    @wraps(func)
    def wrapper(url):
        # Cache key for the content and count
        content_key = f"content:{url}"
        count_key = f"count:{url}"
        
        # Increment the access count
        cache.incr(count_key)
        
        # Check if the content is cached
        cached_content = cache.get(content_key)
        if cached_content:
            print("Returning cached content")
            return cached_content
        
        # If not cached, fetch the content using the original function
        print("Fetching new content")
        content = func(url)
        
        # Cache the content with an expiration time of 10 seconds
        cache.setex(content_key, 10, content)
        
        return content
    return wrapper

@cache_page
def get_page(url: str) -> str:
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    
    # Fetch the page twice to see caching in action
    print(get_page(test_url))
    time.sleep(5)  # Sleep for 5 seconds (less than cache expiry time)
    print(get_page(test_url))
    time.sleep(10)  # Sleep for 10 seconds (more than cache expiry time)
    print(get_page(test_url))

