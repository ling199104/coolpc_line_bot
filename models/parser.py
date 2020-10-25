# encoding: utf8
# import codecs
import requests
import re
from bs4 import BeautifulSoup


class CoolPcCrawler:
    @classmethod
    def get_response(cls) -> BeautifulSoup:
        response = requests.get(
            url="http://www.coolpc.com.tw/evaluate.php",
            params={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache"
            }
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    @classmethod
    def get_data(cls, soup) -> list:
        # [[title_1, header_1, {info_1}, [limited_sale_items], [hot-sale_items], [price_changed_items], [items]]...]]
        text_list = soup.select("tbody#tbdy > tr > td > td")
        data = [[] for _ in range(len(text_list)-1)]
        for i, content in enumerate(text_list):
            if i == 0:  # for the first row only
                # get title
                data[0].append(content.text)
            elif i == 1:  # for the first row only
                # lookahead assertion: match text before \n exclude \n
                compiler = re.compile(r'^\u5171\u6709.+\n')  # 共有...
                # get info
                header = re.match(compiler, content('option')[0].text)
                if header:
                    header = re.sub(r'\u25bc', '', header.group())  # \u25bc = ▼
                    header = re.sub(r'\n', '', header)
                    data[0].append(header)

                    # get the numbers in info
                    info = re.sub(r'(\s+)|(\u25bc)|(\u6a23)', '', header)
                    if info:
                        info_list = info.split('，')
                        info_list = [info for info in info_list]
                        # ex. {'共有商品': '107', '熱賣': '10', '圖片': '106', '討論': '81', '價格異動': '3'}
                        info_dict = {re.sub(r'[0-9]+', '', info): re.sub(r'[\u4e00-\u9fa5]+', '', info)
                                     for info in info_list}  # \u6a23 = 樣
                        data[0].append(info_dict)
                # find limited price
                limited = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text) for option in content('option')
                           if re.findall('\u4e0b\u6bba\u5230', option.text) != []]  # ◆ | ★; \u4e0b\u6bba\u5230 = 下殺到
                if limited:
                    data[0].append(limited)
                else:
                    data[0].append([])
                # find hot-sale item
                hot_sale = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text) for option in content('option')
                            if re.findall(r'\u71b1\u8ce3$', option.text) != []]
                if hot_sale:
                    data[0].append(hot_sale)
                else:
                    data[0].append([])
                # find price changed
                price_changed = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text)
                                 for option in content('option') if re.findall('\u2198', option.text) != []]  # ↘
                if price_changed:
                    data[0].append(price_changed)
                else:
                    data[0].append([])
                # get ride of those numbers in the end of data
                item_list = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text) for option in content('option')
                             if (re.sub(r'\d+', '', option.text) != '' and re.findall(r'\$', option.text) != [])]
                data[0].append(item_list[1:])
            else:
                # get title from list of find_all()
                title = content.text
                compiler = re.compile(r'^.+(?=\n)')
                title_text = re.match(compiler, title)
                if title_text:
                    data[i-1].append(title_text.group())

                # get info
                compiler = re.compile(r'^\u5171\u6709.+\n')  # 共有...
                header = re.match(compiler, content('option')[0].text)
                if header:
                    header = re.sub(r'\u25bc', '', header.group())  # \u25bc = ▼
                    header = re.sub(r'\n', '', header)
                    data[i-1].append(header)
                    # get the numbers in info; \u6a23 = 樣
                    info_list = [info for info in re.sub(r'\s+|\u25bc|\u6a23', '', header).split('，')]
                    # ex. {'共有商品': '107', '熱賣': '10', '圖片': '106', '討論': '81', '價格異動': '3'}
                    info_dict = {re.sub(r'[0-9]+', '', info): re.sub(r'[\u4e00-\u9fa5]+', '', info)
                                 for info in info_list}
                    data[i-1].append(info_dict)
                # find limited price
                limited = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text)
                           for option in content('option')[1:] if re.findall('下殺到', option.text) != []]  # ◆ | ★
                if limited:
                    data[i - 1].append(limited)
                else:
                    data[i - 1].append([])
                # find hot-sale item
                hot_sale = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text)
                            for option in content('option')[1:] if re.findall('熱賣', option.text) != []]
                if hot_sale:
                    data[i - 1].append(hot_sale)
                else:
                    data[i - 1].append([])
                # find price changed
                price_changed = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text)
                                 for option in content('option')[1:] if re.findall('\u2198', option.text) != []]  # ↘
                if price_changed:
                    data[i - 1].append(price_changed)
                else:
                    data[i - 1].append([])
                # get ride of those numbers in the end of data
                item_list = [re.sub(r'(\u3000)|(\u25c6)|(\u2605)|\n', '', option.text) for option in
                             content('option')[1:] if (re.sub(r'\d+', '', option.text) != '' and
                                                       re.findall(r'\$', option.text) != [])]
                data[i-1].append(item_list[1:])
        return data

    @classmethod
    def get_feebee_image(cls, search_keyword: str):
        response = requests.get(
            url="https://feebee.com.tw/s/".format(search_keyword),
            params={
                "q": "旋剛 勁風者 VG5-W (紅)"
            },
            headers={
                "Host": "feebee.com.tw",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "TE": "Trailers"
            }
        )
        response.encoding = 'utf8'
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_analyze = soup.select_one("li > span > a > img")
        return re.sub(r'.+=/|\?\d+', '', pre_analyze['data-src'])


if __name__ == "__main__":  # debug-only
    first_soup = CoolPcCrawler.get_response()
    cool_pc_data = CoolPcCrawler.get_data(first_soup)
    for dataset in cool_pc_data:
        print(dataset[4])
