import os
import requests
import time
from duckduckgo_search import DDGS
from typing import List, Optional

def fetch_web_images(query: str, max_images: int = 1, output_dir: str = "downloaded_images") -> List[str]:
    """
    Searches the web for images matching the query and downloads them.
    Returns a list of local file paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_paths = []
    try:
        with DDGS() as ddgs:
            # Search for images
            results = ddgs.images(
                keywords=query,
                region="wt-wt",
                safesearch="on",
                size="Medium",
                type_none=True,
                max_results=max_images
            )

            for i, res in enumerate(results):
                image_url = res.get("image")
                if not image_url:
                    continue

                try:
                    # Download image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Determine extension
                        ext = image_url.split('.')[-1].split('?')[0].lower()
                        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                            ext = 'jpg'
                        
                        filename = f"web_image_{int(time.time())}_{i}.{ext}"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, "wb") as f:
                            f.write(response.content)
                        
                        image_paths.append(filepath)
                        print(f"[ImageFetcher] Downloaded image: {image_url}")
                except Exception as e:
                    print(f"[ImageFetcher] Failed to download {image_url}: {e}")

    except Exception as e:
        print(f"[ImageFetcher] Error searching for images: {e}")

    return image_paths
