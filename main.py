import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from queue import Queue

# ==============================
# تنظیمات اصلی پروژه
# ==============================
MAX_PAGES = 30          # حداکثر تعداد صفحاتی که خزش می‌کنیم
REQUEST_TIMEOUT = 5      # تایم‌اوت درخواست‌ها (ثانیه)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (TriangleCrawler Research Bot)"
}


# ==============================
# 1) نرمال‌سازی لینک
# حذف fragment و اسلش اضافه
# ==============================
def normalize_url(url):
    parsed = urlparse(url)
    normalized = parsed.scheme + "://" + parsed.netloc + parsed.path
    return normalized.rstrip("/")


# ==============================
# 2) استخراج لینک‌ها از صفحه
# ==============================
def extract_links(url):
    links = set()

    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if "text/html" not in response.headers.get("Content-Type", ""):
            return links  # فقط HTML مهمه

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.scheme in ["http", "https"]:
                links.add(normalize_url(full_url))

    except Exception as e:
        print(f"Error fetching {url} -> {e}")

    return links


# ==============================
# 3) خزش وب و ساخت گراف
# ==============================
def crawl_web(seeds):
    visited = set()
    graph = {}
    queue = Queue()

    for seed in seeds:
        queue.put(normalize_url(seed))

    while not queue.empty() and len(visited) < MAX_PAGES:
        current_url = queue.get()

        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")
        visited.add(current_url)

        links = extract_links(current_url)
        graph[current_url] = links

        for link in links:
            if link not in visited:
                queue.put(link)

    return graph


# ==============================
# 4) پیدا کردن مثلث‌های ارجاعی
# ==============================
def find_triangles(graph):
    triangles = set()

    for a in graph:
        for b in graph[a]:            # a → b
            if b not in graph or a == b:
                continue

            for c in graph[b]:        # b → c
                if c not in graph or b == c or a == c:
                    continue

                if a in graph[c]:     # c → a
                    tri = tuple(sorted([a, b, c]))
                    triangles.add(tri)

    return triangles


# ==============================
# 5) چاپ گراف (اختیاری)
# ==============================
def print_graph(graph):
    print("\n====== LINK GRAPH ======")
    for page, links in graph.items():
        print(f"{page} -> {len(links)} links")


# ==============================
# 6) اجرای اصلی برنامه
# ==============================
if __name__ == "__main__":
    seeds = [
        "https://quera.org/dashboard"
    ]

    print("\n🚀 Starting Crawl...\n")
    graph = crawl_web(seeds)

    print_graph(graph)

    print("\n🔺 Searching for Triangular References...\n")
    triangles = find_triangles(graph)

    if not triangles:
        print("No triangular link patterns found.")
    else:
        print("Found Triangles:")
        for t in triangles:
            print("A → B → C → A :", t)
