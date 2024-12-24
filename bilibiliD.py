import json
import os
import re
import requests
import ffmpeg
from tqdm import tqdm
import subprocess
import platform

class BilibiliDownloader:
    def __init__(self, url, sessdata="", cookies=None, headers=None):
        """
        初始化 Bilibili 下载器

        :param url: Bilibili 视频的网址
        :param sessdata: 用户的 SESSDATA，如果没有可以传空字符串，或者通过 cookies 传递
        :param cookies: 请求时需要使用的 cookies（默认为 None）
        :param headers: 请求时需要使用的 headers（默认为 None）
        """
        # 设置请求 headers
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'referer': 'https://www.bilibili.com/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        # 设置 cookies
        cookies = {
            'SESSDATA': sessdata if sessdata else ''
        }

        self.url = url
        self.sessdata = sessdata
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.video_title = ""
        self.video_url = ""
        self.audio_url = ""
        self.output_path = ""

    def get_sessdata(self):
        """
        获取 SESSDATA
        :return: SESSDATA
        """
        if self.sessdata:
            return self.sessdata
        elif os.path.exists("SESSDATA.txt"):
            # 如果文件存在，读取文件中的 SESSDATA
            with open("SESSDATA.txt", "r") as file:
                sessdata = file.read().strip()
            if len(sessdata) != 222:
                print("SESSDATA.txt 中的 SESSDATA 格式不正确，请检查")
                return ""
            else:
                print("已从 SESSDATA.txt 获取 SESSDATA")
                return sessdata
        else:
            return ""  # 返回空字符串
    def sanitize_filename(self, title):
        """替换非法字符（例如 Windows 系统中的非法字符）"""
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)  # 将非法字符替换为 '_'
        sanitized_title = sanitized_title.strip()  # 去除两端的空格
        sanitized_title = sanitized_title[:50]
        return sanitized_title
    def fetch_video_info(self):
        """从 Bilibili 获取视频信息"""
        try:
            response = requests.get(self.url, cookies=self.cookies, headers=self.headers)
            if response.status_code == 200:
                # 提取视频标题
                self.video_title = self.sanitize_filename(re.findall('<h1 data-title="(.*?)" title="', response.text)[0])

                # 获取视频和音频的下载链接
                video_info = json.loads(re.findall('__playinfo__=(.*?)</script>', response.text)[0])
                self.video_url = video_info['data']['dash']['video'][0]['baseUrl']
                self.audio_url = video_info['data']['dash']['audio'][0]['baseUrl']
                print(f"视频标题：{self.video_title}")
                print(f"视频URL：{self.video_url} 分辨率: {video_info['data']['dash']['video'][0]['width']} * {video_info['data']['dash']['video'][0]['height']}")
                print(f"音频URL：{self.audio_url} 时长: {video_info['data']['dash']['duration']}s")
            else:
                print(f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"获取视频信息时发生错误: {e}")

    def download_file(self, url, filename):
        """下载文件并保存到本地"""
        try:
            os.makedirs('video', exist_ok=True)
            temp_path = os.path.join("video", f"bilibiliVideo", "temp")
            os.makedirs(temp_path, exist_ok=True)

            # 发起请求获取视频文件
            response = requests.get(url, cookies=self.cookies, headers=self.headers, stream=True)

            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                with open(filename, 'wb') as f, tqdm(
                        desc=filename,
                        total=total_size,
                        unit='B',
                        unit_scale=True
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        bar.update(len(data))  # 更新进度条
                        f.write(data)  # 写入文件内容
                print(f"文件已保存为 {filename}")
            else:
                print(f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载文件时发生错误: {e}")

    def check_ffmpeg_installed(self):
        """检查 ffmpeg 是否安装"""
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False

    def combine_video_and_audio(self, video_path, audio_path, output_path):
        """使用 ffmpeg-python 合并视频和音频"""

        if self.check_ffmpeg_installed():
            # 如果 ffmpeg 安装了，使用 ffmpeg 来合并
            print('检测到ffmpeg已安装')
            print('合并视频和音频中...  取决于电脑配置')
            try:
                command = [
                    'ffmpeg',
                    '-i', video_path,  # 输入视频文件
                    '-i', audio_path,  # 输入音频文件
                    '-c:v', 'libx264',  # 视频编解码器
                    '-c:a', 'aac',  # 音频编解码器
                    '-b:a', '192k',  # 设置音频比特率
                    '-strict', 'experimental',  # 允许实验性功能
                    '-preset', 'fast',  # 设置编码速度
                    '-y',  # 自动覆盖输出文件
                    output_path  # 输出文件路径
                ]

                subprocess.run(command, check=True)
                print(f"合并完成，输出文件: {output_path}")

            except subprocess.CalledProcessError as e:
                print(f"FFmpeg 错误: {e}")
            except Exception as e:
                print(f"发生错误: {e}")
            return True
        else:
            print('未检测到ffmpeg')
            system_platform = platform.system()

            if system_platform == 'Windows':
                print(
                    '请安装ffmpeg并设置环境变量，具体步骤参考：https://ffmpeg.org/ windows版本 ： https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2024-12-23-git-6c9218d748-full_build.7z')
            elif system_platform == 'Darwin':  # macOS的系统平台名称是Darwin
                print('请安装ffmpeg并设置环境变量，您可以通过Homebrew安装：\nbrew install ffmpeg')
            else:
                print('当前平台未明确支持，建议访问FFmpeg官方网站：https://ffmpeg.org/download.html')
            return False

    def download_and_merge(self):
            """下载视频和音频并合并"""
            self.fetch_video_info()

            if not self.video_url or not self.audio_url:
                print("视频或音频URL缺失，无法下载或合并")
                return

            # 下载视频和音频
            os.makedirs('video', exist_ok=True)
            temp_path = os.path.join("video",f"bilibiliVideo", "temp")

            video_filename = os.path.join(temp_path,f"{self.video_title}.mp4")
            audio_filename = os.path.join(temp_path,f"{self.video_title}.mp3")

            print(f"开始下载视频: {video_filename}")
            self.download_file(self.video_url, video_filename)

            print(f"开始下载音频: {audio_filename}")
            self.download_file(self.audio_url, audio_filename)

            # 合并视频和音频
            os.makedirs('video', exist_ok=True)
            self.output_path = os.path.join("video", "bilibiliVideo",f"{self.video_title}.mp4")
            is_combined = self.combine_video_and_audio(video_filename, audio_filename, self.output_path)

            if is_combined:
                # 清空temp
                if os.path.exists(temp_path):
                    for file in os.listdir(temp_path):
                        file_path = os.path.join(temp_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    os.rmdir(temp_path)


# 调用类的函数来执行下载任务

def download_bilibili_video(url, sessdata="", cookies=None, headers=None):


    downloader = BilibiliDownloader(url, sessdata, cookies=cookies, headers=headers)

    print(url, sessdata, cookies, headers)
    downloader.download_and_merge()


if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    import argparse

    parser = argparse.ArgumentParser(description="Bilibili Video Downloader")
    parser.add_argument('url', type=str, help="Bilibili 视频 URL")
    parser.add_argument('--sessdata', type=str, default="", help="SESSDATA cookie 参数，若没有请留空")
    args = parser.parse_args()

    # 获取 SESSDATA
    sessdata = args.sessdata or ""

    # 设置 cookies
    cookies = {
        'SESSDATA': sessdata if sessdata else ''
    }

    # 设置请求 headers
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'referer': 'https://www.bilibili.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    # 使用类方法下载并合并视频
    download_bilibili_video(args.url, sessdata, cookies, headers)
