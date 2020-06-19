import requests
import base64
import re
import xlsxwriter
import time
import sys
import urllib.parse
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

requests.packages.urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 OPR/52.0.2871.40',
    'Cookie': '_fofapro_ars_session=542a715870e68564c8584b138da62c15'       # 请输入你的session
}
workbook = xlsxwriter.Workbook(r'C:\Users\sws123\Desktop\fofa-888.xlsx')
worksheet = workbook.add_worksheet('sheet1')
headings = ['hostname', 'port', 'status', 'ssl_domain', 'server', 'title', 'redirect']
data, a, b, c, d, e, f, g = [], [], [], [], [], [], [], []


def get_page(key):
    key_base64 = base64.b64encode(key.encode('utf-8')).decode()
    key_base64 = urllib.parse.quote(key_base64)
    url = f'https://fofa.so/result?page=1&qbase64={key_base64}'
    print(url)
    r = requests.get(url=url, headers=headers, verify=False)
    html = r.text
    response = HtmlResponse(html, body=html, encoding='utf-8')
    selector = Selector(response=response)
    for i in [7, 6, 5, 4, 3, 2, 1]:
        path_xpath = f'normalize-space(//*[@id="will_page"]/a[{i}])'
        page = selector.xpath(path_xpath).extract()
        page = " ".join(page)
        if page and '下一页' not in page:
            break
    if not page:
        page = 1
    return page
    

def get_url(key, count):
    key_base64 = base64.b64encode(key.encode('utf-8')).decode()
    key_base64 = urllib.parse.quote(key_base64)
    scanurl = f'https://fofa.so/result?page={count}&qbase64={key_base64}'
    return scanurl
    
    
def scan(target):
    global count
    global page_count
    count += 1
    leave_count = page_count - count - 1
    print(f'这是第{count}页的内容，还有{leave_count}页的内容：')
    result = ''
    r = requests.get(url=target, headers=headers, verify=False)
    if headers['Cookie'] in str(r.cookies):
        result = True
    html = r.text
    response = HtmlResponse(html, body=html, encoding='utf-8')
    selector = Selector(response=response)
    if result:
        for i in range(2, 12):
            host_xpath = f'normalize-space(//*[@id="ajax_content"]/div/div[{i}]/div[1]/a)'
            port_xpath = f'normalize-space(//*[@id="ajax_content"]/div/div[{i}]/div[1]/div/span[1]/a)'
            title_xpath = f'normalize-space(//*[@id="ajax_content"]/div/div[{i}]/div[2]/div/div[1]/ul/li[1])'
            body_xpath = f'normalize-space(//*[@id="ajax_content"]/div/div[{i}]/div[2]/div/div[2]/div[1])'
            host_result = selector.xpath(host_xpath).extract()
            port_result = selector.xpath(port_xpath).extract()
            title_result = selector.xpath(title_xpath).extract()
            body_result = selector.xpath(body_xpath).extract()
            host = " ".join(host_result)
            port = " ".join(port_result).strip()
            title = " ".join(title_result)
            body = " ".join(body_result)
            if port:
                port = int(port)
            a.append(host)
            b.append(port)
            f.append(title)
            try:
                status = body.split(' ')[1].strip()
                if status not in ['200', '301', '302', '303', '304', '307', '400', '401', '403', '404', '405', '407',
                                  '500', '501', '502', '503', '504', '508']:
                    status = ''
            except:
                status = ''
            if '302' in status:
                redirect_url = re.findall(r'(?<=Location: ).*(?= Set-Cookie:)', body)
                redirect_url = " ".join(redirect_url)
                if not redirect_url:
                    # re.findall(r'[a-zA-Z]+://[^\s]*[.com|.cn]', body)
                    redirect_url = re.findall(r'([a-zA-z]+://[^\s]*)', body)
                    redirect_url = " ".join(redirect_url)
            else:
                redirect_url = ''
            if status:
                status = int(status)
            c.append(status)
            g.append(redirect_url)
            server = re.findall(r'(?<=Server: ).*(?= Set-Cookie:)', body)
            server_list = [' Date:', ' Version:', ' X-Powered-By:', ' X-AspNet-Version:', ' X-Aspnet-Version:',
                           ' X-Content-Type-Options:'
                           ]
            server = " ".join(server)
            i = -1
            while not server:
                i += 1
                server = re.findall(f'(?<=Server: ).*(?={server_list[i]})', body)
                server = " ".join(server)
                for name in server_list:
                    if name in server:
                        server = ''
                if i >= len(server_list) - 1:
                    break
            e.append(server)
            ssl_domain = re.findall(r'(?<=CommonName: ).*(?=Subject Public)', body)
            ssl_domain = " ".join(ssl_domain).strip()
            try:
                ssl_domain = ssl_domain.split(' CommonName: ')[1]
            except:
                ssl_domain = ''
            d.append(ssl_domain)
            print(f'{ssl_domain}\t{host}\t{port}\t{status}\t{server}\t{title}\t{redirect_url}')
            if '出错了' in html:
                print('某个地方出现了问题，请查看html代码')
                print(html)
                sys.exit()
    else:
        print('cookie无效，请重新获取cookie')
        

def main():
    global count
    global page_count
    count = 0
    key = 'title="华住酒店"'                # 请输入查询的关键词
    page_count = get_page(key)
    page_count = int(page_count) + 1
    for page in range(1, page_count):
        url = get_url(key, page)
        scan(url)
        time.sleep(4)
    data.append(a)
    data.append(b)
    data.append(c)
    data.append(d)
    data.append(e)
    data.append(f)
    data.append(g)
    worksheet.write_row('A1', headings)
    worksheet.write_column('A2', data[0])
    worksheet.write_column('B2', data[1])
    worksheet.write_column('C2', data[2])
    worksheet.write_column('D2', data[3])
    worksheet.write_column('E2', data[4])
    worksheet.write_column('F2', data[5])
    worksheet.write_column('G2', data[6])
    workbook.close()
    
    
if __name__ == '__main__':
    main()
