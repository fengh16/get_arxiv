import requests
from time import time, sleep
from xml.etree import ElementTree as ET
from random import random, choice
from os import makedirs


# get search term
a = 'graph'

step = 200  # 每一次取200篇

start = 6400   # 从start开始
timestamp = time()
makedirs(f'output-{timestamp}', exist_ok=True)
makedirs(f'raw-{timestamp}', exist_ok=True)

# 定义一个包含多个 User-Agent 字符串的列表
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36'
]

while True:
    # URL of the XML object
    url = "http://export.arxiv.org/api/query?search_query=all:%s&sortBy=lastUpdatedDate&sortOrder=descending&start=%d&max_results=%d" % (a.lower().replace(' ','%20'), start, step)
    print(url)

    try:
        if random() < 0.9:
            # 随机选择一个 User-Agent
            selected_user_agent = choice(user_agents)

            headers = {
                'User-Agent': selected_user_agent
            }
        else:
            headers = {}
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
    except:
        print("出问题了，等一会")
        sleep(1000 + random() * 2000)
        continue

    # Parse the XML response
    content_returned = response.content
    root = ET.fromstring(content_returned)
    with open(f"raw-{timestamp}\\{a}-{start}.xml", "wb") as file:
        file.write(content_returned)

    # Namespace dictionary to find elements
    namespaces = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

    get_number = 0

    # Open the output file with UTF-8 encoding
    with open("output-%s\\%s-%d.md" % (timestamp, a, start), "w", encoding='utf-8') as file:
        # Iterate over each entry in the XML data
        for entry in root.findall('atom:entry', namespaces):
            try:
                # Extract and write the title
                title = entry.find('atom:title', namespaces).text
                title = ' '.join(title.split())  # Replace newlines and superfluous whitespace with a single space
                file.write(f"# {title}\n\n")

                # Extract and write the link to the paper
                id = entry.find('atom:id', namespaces).text
                file.write(f"[Link to the paper]({id})\n\n")

                # Extract and write the authors
                authors = entry.findall('atom:author', namespaces)
                file.write("## Authors\n")
                for author in authors:
                    name = author.find('atom:name', namespaces).text
                    file.write(f"- {name}\n")
                file.write("\n")

                # Extract and write the summary
                summary = entry.find('atom:summary', namespaces).text
                file.write(f"## Summary\n{summary}\n\n")

                get_number += 1
            except:
                pass
    
    if get_number == 0:
        # 没有找到，可能超时了吧
        print(content_returned.decode())
        print(content_returned.decode().count("<summary>"))
        print("超时了吧，休息一下吧")
        sleep(1000 + random() * 2000)
    elif get_number < step:
        # 找完了
        print(content_returned.decode())    
        print(content_returned.decode().count("<summary>"))
        print("找完了")
        break
    start += step
    print("累计找到了%d篇" % start)
    sleep(30 + random() * 200)  # 避免被封
