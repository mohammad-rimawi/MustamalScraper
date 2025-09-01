import asyncio
import sys
import os
from playwright.async_api import async_playwright
import json
import random
from datetime import datetime

if sys.platform.startswith('win'):
    os.system('chcp 65001')
    sys.stdout.reconfigure(encoding='utf-8')

async def scrape_mstaml_smart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.mstaml.com")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)

        known_product_links = [
            "https://www.mstaml.com/sa/product/الدما...؟id=4536075...",
            "https://www.mstaml.com/sa/product/الرياض...؟id=4536074...",
            "https://www.mstaml.com/sa/product/الرياض...؟id=4536072..."
        ]

        product_links = known_product_links.copy()

        try:
            additional_links = await page.locator("a[href*='/product/']").all()
            for link in additional_links:
                href = await link.get_attribute('href')
                if href and '/product/' in href:
                    full_url = href if href.startswith('http') else f"https://www.mstaml.com{href}"
                    if full_url not in product_links:
                        product_links.append(full_url)
        except Exception:
            pass

        categories = [
            "https://www.mstaml.com/market/سيارات?type=4",
            "https://www.mstaml.com/market/جوالات",
            "https://www.mstaml.com/market/إلكترونيات"
        ]

        for category_url in categories:
            try:
                await page.goto(category_url)
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(3000)
                category_products = await page.locator("a[href*='/product/']").all()
                for prod_link in category_products:
                    href = await prod_link.get_attribute('href')
                    if href and '/product/' in href:
                        full_url = href if href.startswith('http') else f"https://www.mstaml.com{href}"
                        if full_url not in product_links:
                            product_links.append(full_url)
                await page.wait_for_timeout(2000)
            except Exception:
                continue

        product_links = list(set(product_links))

        all_products_data = []
        failed_products = []

        for i, link in enumerate(product_links):
            try:
                await page.goto(link)
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(3000)

                product_data = {
                    'id': i + 1,
                    'url': link,
                    'scraped_at': datetime.now().isoformat(),
                    'title': '',
                    'price': '',
                    'description': '',
                    'location': '',
                    'seller_info': '',
                    'category': '',
                    'images': [],
                    'contact_info': '',
                    'post_details': {}
                }

                try:
                    title_selectors = ['h1', '[class*="title"]', '[class*="heading"]', 'title']
                    for selector in title_selectors:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            title_text = await element.text_content()
                            if title_text and len(title_text.strip()) > 5:
                                product_data['title'] = title_text.strip()
                                break
                except:
                    pass

                try:
                    price_elements = await page.locator('//*[contains(text(), "ريال") or contains(text(), "درهم") or contains(text(), "دولار")]').all()
                    for price_elem in price_elements:
                        price_text = await price_elem.text_content()
                        if price_text and any(char.isdigit() for char in price_text):
                            product_data['price'] = price_text.strip()
                            break
                    if not product_data['price']:
                        price_selectors = ['[class*="price"]', '[class*="cost"]', '[class*="amount"]']
                        for selector in price_selectors:
                            element = page.locator(selector).first
                            if await element.count() > 0:
                                price_text = await element.text_content()
                                if price_text and price_text.strip():
                                    product_data['price'] = price_text.strip()
                                    break
                except:
                    pass

                try:
                    if '/sa/product/' in link:
                        url_parts = link.split('/')
                        if len(url_parts) > 4:
                            import urllib.parse
                            encoded_location = url_parts[4]
                            try:
                                decoded_location = urllib.parse.unquote(encoded_location)
                                product_data['location'] = decoded_location
                            except:
                                product_data['location'] = encoded_location

                    location_selectors = ['[class*="location"]', '[class*="city"]', '[class*="area"]']
                    for selector in location_selectors:
                        element = page.locator(selector).first
                        if await element.count() > 0:
                            location_text = await element.text_content()
                            if location_text and location_text.strip():
                                product_data['location'] = location_text.strip()
                                break
                except:
                    pass

                try:
                    desc_selectors = [
                        '[class*="description"]',
                        '[class*="detail"]',
                        '[class*="content"]',
                        'p',
                        'div[class*="text"]'
                    ]
                    for selector in desc_selectors:
                        elements = await page.locator(selector).all()
                        for element in elements:
                            desc_text = await element.text_content()
                            if desc_text and len(desc_text.strip()) > 20:
                                product_data['description'] = desc_text.strip()
                                break
                        if product_data['description']:
                            break
                except:
                    pass

                try:
                    images = await page.locator('img').all()
                    for img in images:
                        src = await img.get_attribute('src')
                        if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            if not any(skip in src.lower() for skip in ['logo', 'icon', 'avatar']):
                                full_img_url = src if src.startswith('http') else f"https://www.mstaml.com{src}"
                                if full_img_url not in product_data['images']:
                                    product_data['images'].append(full_img_url)
                except:
                    pass

                all_products_data.append(product_data)

                if (i + 1) % 5 == 0:
                    with open(f'mstaml_backup_{i+1}.json', 'w', encoding='utf-8') as f:
                        json.dump(all_products_data, f, ensure_ascii=False, indent=2)

                await page.wait_for_timeout(random.randint(2000, 4000))

            except Exception as e:
                failed_products.append({'index': i + 1, 'url': link, 'error': str(e)})
                continue

        final_data = {
            'scraping_info': {
                'scraped_at': datetime.now().isoformat(),
                'total_found': len(product_links),
                'successful_scrapes': len(all_products_data),
                'failed_scrapes': len(failed_products),
                'success_rate': f"{(len(all_products_data) / len(product_links) * 100):.1f}%" if product_links else "0%"
            },
            'products': all_products_data,
            'failed_products': failed_products
        }

        with open('mstaml_products_final.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        try:
            import pandas as pd
            if all_products_data:
                df = pd.DataFrame(all_products_data)
                df.to_csv('mstaml_products_final.csv', index=False, encoding='utf-8-sig')
        except ImportError:
            pass

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_mstaml_smart())
