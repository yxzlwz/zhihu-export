import re
from json import load
from pathlib import Path
from time import sleep

from requests import Session
from bs4 import BeautifulSoup
from html2text import html2text

file_dir = Path(__file__).parent.resolve()
data_dir = file_dir / 'answer'

use_optimize = True

zhihu_data_name = 'zhihu_data.json'

sleep_seconds = 4

_cookies = ''

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def get_answer(session: Session, url):
    name = url.split("/")[-1]

    html_file = data_dir / f'{name}.html'

    need_sleep = False
    if html_file.exists():
        print('【本地缓存】', end='...')
        html = html_file.read_text(encoding='utf-8')
    else:
        print('【网络请求】', end='...')
        r = session.get(url)
        need_sleep = True
        html = r.text
        with open(data_dir / f'{name}.html', 'w', encoding='utf-8') as f:
            f.write(html)

    soup = BeautifulSoup(html, 'html.parser')

    RichContent_inner = soup.find('div', class_='RichContent-inner')
    html = RichContent_inner.decode_contents()

    md = html2text(html)

    if use_optimize:
        name = name + '_optimized'

        # 去除SVG标签
        svg_pattern = re.compile(
            r"!\[\]\(data:image/svg\+xml;utf8.+<svg.+xmlns='http://www.w3.org/2000/svg'.+width='\d+'.+height='\d+'></svg>\)",
            re.DOTALL)
        md = re.sub(svg_pattern, '', md)

        # 知乎链接卡片优化
        md = re.sub(r'^\s*\[\]\((https?://[^\)]+)\)\s*$',
                    r'[\1](\1)',
                    md,
                    flags=re.MULTILINE)

        # 修改分割线样式，个人习惯
        md = md.replace('* * *\n', '---\n')

        # 去除末尾的空字符
        while md[-1] in (' ', '\n'):
            md = md[:-1]
        md += '\n'

    with open(data_dir / f'{name}.md', 'w', encoding='utf-8') as f:
        f.write(md)

    print(f'保存成功', end='')

    if need_sleep:
        print(f'，等待{sleep_seconds}秒进行下一个')
        sleep(sleep_seconds)
    else:
        print('')


def main():
    data_dir.mkdir(parents=True, exist_ok=True)

    cookies = {}
    for cookie in _cookies.split('; '):
        key = cookie[:cookie.index('=')]
        value = cookie[cookie.index('=') + 1:]
        cookies[key] = value

    session = Session()
    session.cookies.update(cookies)
    session.headers.update({'User-Agent': user_agent})

    with open(file_dir / zhihu_data_name, 'r', encoding='utf-8') as f:
        data = load(f)

    total = len(data)
    cnt = 0

    err = []

    for ans in data:
        cnt += 1

        print(f'开始运行{cnt}/{total}，HTML来源为', end='')

        try:
            get_answer(session, ans['answer_url'])
        except Exception as e:
            print('出错了！')
            print(e)
            print(ans)
            err.append({'ans': ans, 'e': e})


if __name__ == '__main__':
    main()
