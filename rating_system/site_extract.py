import requests
from bs4 import BeautifulSoup

# 定义 Sitemap 的 URL
sitemap_url = "https://wiki.seeedstudio.com/sitemap.xml"

# 获取 Sitemap 内容
response = requests.get(sitemap_url)
if response.status_code == 200:
    # 解析 XML 内容
    soup = BeautifulSoup(response.content, "xml")
    urls = [url.text for url in soup.find_all("loc")]
    
    # 计算总网址数
    total_urls = len(urls)
    print(f"总共找到 {total_urls} 个网址")
    
    # 将所有 URL 保存到 txt 文件
    output_file = "sitemap_urls.txt"
    with open(output_file, "w", encoding="utf-8") as file:
        for url in urls:
            file.write(url + "\n")
    
    print(f"所有 URL 已保存到 {output_file}")
else:
    print(f"无法访问 Sitemap 文件，状态码: {response.status_code}")
