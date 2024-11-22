# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Remote file reader.

A loader that fetches any remote page or file by URL and retrieves child pages with certain constraints. The class also parses the contents of each page and provides access to the parsed data.
"""
from typing import Any, Dict, List, Optional, Union

from nextpy.ai import download_loader
from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode
from security import safe_requests


class RemoteDepthReader(BaseReader):
    def __init__(
        self,
        *args: Any,
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        depth: int = 1,
        domain_lock: bool = False,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self.file_extractor = file_extractor
        self.depth = depth
        self.domain_lock = domain_lock

    def load_data(self, url: str) -> List[DocumentNode]:
        from tqdm.auto import tqdm

        """Parse whatever is at the URL.""" ""
        try:
            from nextpy.ai.rag.document_loaders.utils import import_loader

            RemoteReader = import_loader("RemoteReader")
        except ImportError:
            RemoteReader = download_loader("RemoteReader")
        remote_reader = RemoteReader(file_extractor=self.file_extractor)
        documents = []
        links = self.get_links(url)
        urls = {-1: [url]}  # -1 is the starting point
        links_visited = []
        for i in range(self.depth + 1):
            urls[i] = []
            new_links = []
            print(f"Reading links at depth {i}...")
            for link in tqdm(links):
                """Checking if the link belongs the provided domain."""
                if (self.domain_lock and link.find(url) > -1) or (not self.domain_lock):
                    print("Loading link: " + link)
                    if link in links_visited:
                        continue
                    if link:
                        urls[i].append(link)
                        new_links.extend(self.get_links(link))
                    links_visited.append(link)
                else:
                    print("Link ignored: " + link)
            new_links = list(set(new_links))
            links = new_links
        print(f"Found {len(urls)} links at depth {self.depth}.")
        for depth_i in urls:
            for url in urls[depth_i]:
                try:
                    documents.extend(remote_reader.load_data(url))
                except Exception as e:
                    print(f"Error reading {url} at depth {depth_i}: {e}")
                    continue

        return documents

    @staticmethod
    def is_url(href) -> bool:
        """Check if a link is a URL."""
        return href.startswith("http")

    def get_links(self, url) -> List[str]:
        from urllib.parse import urljoin, urlparse, urlunparse

        from bs4 import BeautifulSoup

        """Get all links from a page."""
        page = safe_requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        links = soup.find_all("a")
        result = []
        for link in links:
            href = link if isinstance(link, str) else link.get("href")
            if href is not None and not self.is_url(href):
                href = urljoin(url, href)

            url_parsed = urlparse(href)
            url_without_query_string = urlunparse(
                (url_parsed.scheme, url_parsed.netloc, url_parsed.path, "", "", "")
            )

            if (
                url_without_query_string not in result
                and url_without_query_string
                and url_without_query_string.startswith("http")
            ):
                result.append(url_without_query_string)
        return result
