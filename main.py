import requests
from bs4 import BeautifulSoup

# 你要抓取的实时 URL
url = 'https://steamcommunity.com/market/listings/730/Desert%20Eagle%20%7C%20Printstream%20(Field-Tested)'

# 模拟浏览器的 Headers，防止被 Steam 屏蔽
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # 1. 获取实时 HTML
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # 如果请求失败 (例如 403, 404, 500), 会抛出异常
    
    html = response.text
    
    # 2. 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 3. 查找父元素
    search_results = soup.find(id='searchResultsRows')
    
    if search_results:
        # 4. 查找第二个直属 div
        # 使用 recursive=False 确保只查找直属子元素
        direct_divs = search_results.find_all('div', recursive=False)
        
        if len(direct_divs) >= 2:
            # Python 列表索引从 0 开始，第二个是 [1]
            second_item = direct_divs[1] 
            
            # 5. 查找价格元素
            price_element = second_item.find(class_='market_listing_price_without_fee')
            
            if price_element:
                price = price_element.get_text(strip=True)
                print(f"成功获取价格: {price}")
            else:
                print("错误: 未在第二个物品中找到价格元素。")
        else:
            print(f"错误: 找到了 'searchResultsRows'，但直属 'div' 数量不足两个 (只找到 {len(direct_divs)} 个)。")
    else:
        print("错误: 未能在页面中找到 'searchResultsRows' 元素。")

except requests.exceptions.RequestException as e:
    print(f"请求网页时出错: {e}")
except Exception as e:
    print(f"脚本执行时发生意外错误: {e}")