import requests
from bs4 import BeautifulSoup
import os
import re

def send_to_telegram(message):
    """发送消息到 Telegram"""
    
    # 从 GitHub Actions 环境变量中读取 Secrets
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("错误: 未设置 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 环境变量。")
        return

    # Telegram Bot API 的 URL
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 要发送的数据
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status() # 确保请求成功
        print("成功发送消息到 Telegram。")
    except requests.exceptions.RequestException as e:
        print(f"发送 Telegram 消息时出错: {e}")


def get_usd_to_cny_rate():
    try:
        response = requests.get('https://api.frankfurter.app/latest?from=USD&to=CNY', timeout=5)
        response.raise_for_status()
        data = response.json()
        
        rate = data.get('rates', {}).get('CNY')
        if rate:
            print(f"成功获取汇率: 1 USD = {rate} CNY")
            return float(rate)
        else:
            print("错误: 汇率 API 响应中未找到 CNY 汇率。")
            return None
    except requests.exceptions.RequestException as e:
        print(f"获取汇率时出错: {e}")
        return None


# --- 你的原始抓取逻辑 ---

# 你要抓取的实时 URL
item_name = "Desert Eagle | Printstream (Field-Tested)"
item_url = 'https://steamcommunity.com/market/listings/730/Desert%20Eagle%20%7C%20Printstream%20(Field-Tested)'

# 模拟浏览器的 Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    print(f"正在抓取 {item_name} 的价格...")
    response = requests.get(item_url, headers=headers, timeout=10)
    response.raise_for_status()
    
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    search_results = soup.find(id='searchResultsRows')
    
    if search_results:
        direct_divs = search_results.find_all('div', recursive=False)
        
        if len(direct_divs) >= 2:
            second_item = direct_divs[1]
            price_element = second_item.find(class_='market_listing_price_without_fee')
            
            if price_element:
                # 1. 获取价格字符串，例如 "$150.99"
                usd_price_string = price_element.get_text(strip=True)
                
                # 2. 清理字符串，只保留数字和小数点
                cleaned_price_string = re.sub(r"[^\d\.]", "", usd_price_string)
                usd_price = float(cleaned_price_string)
                print(f"成功获取 USD 价格: ${usd_price:.2f}")

                # 3. 获取实时汇率
                rate = get_usd_to_cny_rate()
                
                if rate:
                    # 4. 计算人民币价格
                    cny_price = usd_price * rate
                    print(f"换算后 CNY 价格: ¥{cny_price:.2f}")
                    
                    # 5. 发送 Telegram 消息
                    message_content = (
                        f"**Steam 价格提醒**\n\n"
                        f"**物品:** {item_name}\n"
                        f"**原始价格 (USD):** `${usd_price:.2f}`\n"
                        f"**换算价格 (CNY):** `¥{cny_price:.2f}`\n"
                        f"*(汇率: 1 USD ≈ {rate:.4f} CNY)*"
                    )
                    send_to_telegram(message_content)
                else:
                    # 汇率获取失败，但仍然发送 USD 价格
                    print("获取汇率失败，仅发送 USD 价格。")
                    send_to_telegram(f"抓取 {item_name} 成功。\n原始价格 (USD): `${usd_price:.2f}`\n(获取 CNY 汇率失败)")
                
            else:
                print("错误: 未在第二个物品中找到价格元素。")
                send_to_telegram(f"抓取 {item_name} 失败: 未找到价格元素。")
        else:
            print(f"错误: 找到了 'searchResultsRows'，但直属 'div' 数量不足两个。")
            send_to_telegram(f"抓取 {item_name} 失败: 直属 div 数量不足。")
    else:
        print("错误: 未能在页面中找到 'searchResultsRows' 元素。")
        send_to_telegram(f"抓取 {item_name} 失败: 页面结构可能已更改 (未找到 'searchResultsRows')。")

except requests.exceptions.RequestException as e:
    print(f"请求网页时出错: {e}")
    send_to_telegram(f"抓取 {item_name} 失败: 请求网页时出错: {e}")
except Exception as e:
    print(f"脚本执行时发生意外错误: {e}")
    send_to_telegram(f"抓取 {item_name} 失败: 脚本发生意外错误: {e}")