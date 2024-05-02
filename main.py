import datetime
import re
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("파라미터부족")
        sys.exit(1)

    elif len(sys.argv) == 4:
        mallname = sys.argv[1].lower()
        sheetname = sys.argv[2]
        fileadress = sys.argv[3]

        # print('1', mallname)
        # print('2', sheetname)
        # print('3', fileadress)
        if sheetname == 'price':
            sheetname = '가격순위'

        df = pd.read_excel(fileadress, sheet_name=sheetname)

        df['productName'] = df['productName'].astype(str)
        df['price'] = df['price'].astype(str)

        print('루프시작')
        for index, row in df.iterrows():
            print(index,'번째')
            url = row['url']
            print('url', url)
            response = requests.get(url)
            time.sleep(0.3)  # 5초 대기
            now = datetime.datetime.now()
            current_time = now.strftime("%Y-%m-%d %I:%M:%S %p")

            if response.status_code == 200:
                # 웹 페이지 파싱
                soup = BeautifulSoup(response.text, 'html.parser')

                try:
                    product_title = soup.select('#itemcase_basic > div.box__item-title > h1')[0].text
                    df.loc[index, 'productName'] = product_title
                    df.loc[index, 'collect'] = 'Y'
                    df.loc[index, 'commerceType'] = 'GMARKET'
                    df.loc[index, 'collectionDate'] = current_time
                except Exception as e:
                    df.loc[index, 'productName'] = 'url없음'
                    df.loc[index, 'collect'] = 'N'
                    df.loc[index, 'commerceType'] = 'GMARKET'
                    df.loc[index, 'collectionDate'] = current_time
                    print('url 없음')

                try:
                    list_price = soup.select('#itemcase_basic > div.box__item-title > div.price > span:nth-child(2) > span.price_original > span.text__price')[0].text
                except Exception as e:
                    df.loc[index, 'listPrice'] = '-'
                    print('원래가격 없음')

                try:
                    product_price = soup.select('#itemcase_basic > div.box__item-title > div.price > '
                                                'span.price_innerwrap > strong')[0].text
                    df.loc[index, 'price'] = product_price

                except Exception as e:
                    df.loc[index, 'price'] = '-'
                    print('가격 없음')

                try:
                    discount_price =  soup.select('#itemcase_basic > div.box__item-title > div.price > span.price_innerwrap.price_innerwrap-coupon > strong')[0].text
                    df.loc[index, 'discountPrice'] = discount_price
                    df.loc[index, 'discountPriceCommerce'] = discount_price
                    df.loc[index, 'totalPrice'] = discount_price
                except Exception as e:
                    df.loc[index, 'discountPrice'] = '-'
                    df.loc[index, 'discountPriceCommerce'] = '-'
                    df.loc[index, 'totalPrice'] = '-'
                    print('할인가격 없음')

                try:
                    star_count = soup.select('#itemcase_basic > div.box__item-title > div.box__rating-information > div > span')[0].text
                    number = int(re.sub('[^0-9]', '', star_count))
                    df.loc[index, 'starScore'] = number
                except Exception as e:
                    df.loc[index, 'starScore'] = '-'
                    print('별점 없음')

                try:
                    sale_company = soup.select('#vip-tab_exchange > div.box__exchange-guide > div:nth-child(6) > ul > li:nth-child(1) > span')[0].text
                    df.loc[index, 'saleCompany'] = sale_company
                except Exception as e:
                    df.loc[index, 'saleCompany'] = '-'
                    print('컴퍼니 없음')

                try:
                    delivery_fee = soup.select('')[0].text
                    df.loc[index, 'deliveryPrice'] = delivery_fee
                except Exception as e:
                    df.loc[index, 'deliveryPrice'] = '-'
                    print('배송비 없음')

                try:
                    brand_name = soup.select('#container > div.item-topinfowrap > div.item-topinfo.item-topinfo--additional.box__item-info--vip > div.item-topinfo_headline > p > span.text__brand > span.text')[0].text
                    df.loc[index, 'brandName'] = brand_name
                except Exception as e:
                    df.loc[index, 'brandName'] = '-'
                    print('브랜드 없음')

                try:
                    first = soup.select('body > div.location-navi > ul > li:nth-child(1) > a')[0].text
                    second = soup.select('body > div.location-navi > ul > li:nth-child(2) > a')[0].text
                    third = soup.select('body > div.location-navi > ul > li:nth-child(3) > a')[0].text
                    forth = soup.select('body > div.location-navi > ul > li.on > a')[0].text
                    full = first + ',' + second + ',' + third + ',' + forth
                    df.loc[index, 'category'] = full
                except Exception as e:
                    df.loc[index, 'category'] = '-'
                    print('뎁스 없음')

            else:
                print(f"Failed to fetch URL: {url}")

        # print(df)
        new_file_path = "C:\\Users\\Rainbow Brain\\Desktop\\new_file.xlsx"
        df.to_excel(new_file_path, index=False)  # index=False로 설정하여 인덱스를 저장하지 않습니다.
        print(f"데이터프레임이 {new_file_path} 파일로 저장되었습니다.")

# python main.py gmarket price "C:\Users\Rainbow Brain\Desktop\PEB01_Gmarket_Result_DB.xlsx"
