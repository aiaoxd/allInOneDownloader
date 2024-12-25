import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


# --- 辅助函数 ---

def save_video_with_url_and_title(url, title, video_folder_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('Content-Length', 0))

    sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)[:50]
    video_path = os.path.join(video_folder_path, f"{sanitized_title}.mp4")

    with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {sanitized_title}.mp4") as pbar:
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    print(f"Downloaded: {video_path}")


def extract_url_from_text(text):
    pattern = r'https://v\.kuaishou\.com/[a-zA-Z0-9]+'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None


def get_real_url_from_kuaishou(short_url):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        response = requests.get(short_url, headers=headers, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"Error: {e}")
        return None


# --- 快手下载器类 ---

class KuaishouDownloader:

    def __init__(self, url, video_folder='video/kuaishouVideo'):
        self.url = url
        self.video_folder = video_folder
        self.cookies = {
        }
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def download_video_with_shareurl(self):
        response = requests.get(self.url, cookies=self.cookies, headers=self.headers)
        print(response)

        try:
            video_url = re.findall("\"url\":\"(.*?)\"", response.text)[0]
        except Exception as e:
            video_url = re.findall("\"photoUrl\"\"(.*?)\"", response.text)[0]

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "没有找到 title 标签"

        try:
            vlogger_name = re.findall("@(.*?)\(", response.text)[0]
        except Exception as e:
            vlogger_name = \
            re.findall("class=\"profile-user-name-title\" data-v-f52f6230>(.*?)</span><span", response.text)[0]
            vlogger_name = vlogger_name.strip()

        vlogger_path = os.path.join(self.video_folder, vlogger_name)
        os.makedirs(vlogger_path, exist_ok=True)

        video_url = video_url.encode('utf-8').decode('unicode_escape')
        save_video_with_url_and_title(video_url, title, vlogger_path)



# --- 主程序 ---

def main():

    url = input("请输入视频URL: ")
    print("正在下载快手视频...")
    kuaishou_downloader = KuaishouDownloader(url)
    kuaishou_downloader.download_video_with_shareurl()
    print("快手视频下载完成！")


if __name__ == '__main__':
    main()
