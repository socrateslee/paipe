'''
Crawl HTML pages under a URL path, convert to Markdown, and archive into a single string.
'''

import httpx
from markdownify import markdownify
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def md(html):
    try:
        return markdownify(html)
    except RecursiveError:
        return ''


def crawl_and_archive(start_url: str, max_pages: int = 10, root_element_selector: str = "") -> str:
    """
    Crawl HTML pages starting from start_url, convert each to Markdown, and archive them.
    
    Args:
        start_url: The URL to start crawling from.
        max_pages: Maximum number of pages to crawl.
        
    Returns:
        A string containing all archived Markdown content.
    """
    visited = set()
    to_visit = [start_url]
    archive = []
    
    base_path = urlparse(start_url).path
    
    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            response = httpx.get(url)
            response.raise_for_status()
        except httpx.HTTPError:
            continue
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else url
        
        # Convert HTML to Markdown
        if root_element_selector:
            soup = BeautifulSoup(html, 'html.parser')
            root_element = soup.select_one(root_element_selector)
            if root_element:
                markdown_content = md(str(root_element))
            else:
                markdown_content = md(html)
        else:
            markdown_content = md(html)
        
        # Format the archive block
        archive_block = f'```` {url}\n# {title}\n\n{markdown_content}\n````\n\n'
        archive.append(archive_block)
        
        # Extract and queue links
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)
            # Check if same base path and not already visited/queued
            if parsed_url.path.startswith(base_path):
                if absolute_url not in visited and absolute_url not in to_visit:
                    to_visit.append(absolute_url)
        
        visited.add(url)
    
    return '\n'.join(archive).strip()