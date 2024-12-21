import re
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
import threading
import queue  # 导入队列模块

# 引入各个平台的视频下载类
from bilibiliD import BilibiliDownloader  # 假设已经修改为类形式
from douyinD import DouyinDownloader  # 假设有一个类似的抖音下载类
from youtubeD import YouTubeDownloader  # 假设有一个类似的 YouTube 下载类

# 定义用于识别视频平台的正则表达式
def identify_platform(url):
    if "douyin.com" in url:
        return 'douyin'
    elif re.match(r'https://www\.bilibili\.com/video/', f"{url}") :
        return 'bilibili'
    elif re.match(r'https://www\.youtube\.com/watch\?v=', f"{url}") :
        return 'youtube'
    else:
        return 'unknown'

# 提取有效的 URL
def extract_valid_url(text):
    urls = re.findall(r'https?://[^\s]+', text)
    return urls[0] if urls else None

# 处理抖音短链接，获取实际的视频 URL
def get_douyin_video_url(short_url):
    return short_url

def get_script_path(script_name):
    if getattr(sys, 'frozen', False):  # 如果是打包后的 EXE 文件
        # 获取打包后的路径
        bundle_dir = os.path.dirname(sys.executable)
    else:
        # 如果是源代码，返回当前目录
        bundle_dir = os.path.dirname(__file__)

    return os.path.join(bundle_dir, script_name)

# 修改 download_video_async 函数
def download_video_async(platform, url, log_queue):
    try:
        if platform == 'douyin':
            log_queue.put("正在下载抖音视频...\n")
            # 使用 DouyinDownloader 类进行下载
            douyin_downloader = DouyinDownloader(url)
            douyin_downloader.start_download()
            log_queue.put("抖音视频下载完成！\n")
        elif platform == 'bilibili':
            log_queue.put("正在下载哔哩哔哩视频...\n")
            # 使用 BilibiliDownloader 类进行下载
            bilibili_downloader = BilibiliDownloader(url)
            bilibili_downloader.download_and_merge()
            log_queue.put("哔哩哔哩视频下载完成！\n")
        elif platform == 'youtube':
            log_queue.put("正在下载 YouTube 视频...\n")
            # 使用 YouTubeDownloader 类进行下载
            youtube_downloader = YouTubeDownloader(url)
            youtube_downloader.download_video()
            log_queue.put("YouTube 视频下载完成！\n")
        else:
            log_queue.put("未知平台，无法下载视频！\n")
    except Exception as e:
        log_queue.put(f"发生错误: {e}\n")

# 用于更新日志框的函数
def update_log(log_text_widget, log_queue):
    try:
        while True:
            log_message = log_queue.get_nowait()  # 非阻塞地获取队列中的日志消息
            log_text_widget.insert(tk.END, log_message)
            log_text_widget.yview(tk.END)  # 自动滚动到最新日志
    except queue.Empty:
        pass

# 创建并启动 GUI
def start_gui():
    def on_download_button_click():
        video_url_input = url_entry.get().strip()

        log_text_widget.delete(1.0, tk.END)  # 每次点击下载按钮时，清空日志框

        video_url = extract_valid_url(video_url_input)
        if not video_url:
            messagebox.showerror("错误", "无效的视频 URL！")
            return

        if 'v.douyin.com' in video_url:
            video_url = get_douyin_video_url(video_url)

        platform = identify_platform(video_url)

        if platform == 'unknown':
            messagebox.showerror("错误", "无法识别该视频平台，请提供有效的 Douyin、Bilibili 或 YouTube 视频链接。")
        else:
            download_thread = threading.Thread(target=download_video_async, args=(platform, video_url, log_queue))
            download_thread.start()

    window = tk.Tk()
    window.title("视频下载器")
    window.geometry("600x400")

    tk.Label(window, text="请输入视频 URL:").pack(pady=10)
    url_entry = tk.Entry(window, width=50)
    url_entry.pack(pady=10)

    download_button = tk.Button(window, text="下载视频", command=on_download_button_click)
    download_button.pack(pady=20)

    log_text_widget = scrolledtext.ScrolledText(window, width=70, height=10)
    log_text_widget.pack(pady=10)

    # 设置队列用于线程间通信
    log_queue = queue.Queue()

    # 启动一个线程用于更新日志框
    def log_updater():
        update_log(log_text_widget, log_queue)
        window.after(100, log_updater)  # 每100毫秒调用一次更新函数

    log_updater()  # 启动日志更新器

    window.mainloop()

if __name__ == "__main__":
    start_gui()
