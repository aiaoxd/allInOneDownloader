import re
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import filedialog
import threading
import queue  # 导入队列模块
import webbrowser  # 用于打开文件夹
import time  # 用于模拟下载进度
from tkinter import ttk

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
    elif re.match(r'https://www\.youtube\.com', f"{url}") :
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

# 将 print 重定向到队列
class PrintRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, message):
        if message != "\n":  # 忽略空行
            self.queue.put(message)

    def flush(self):
        pass  # 需要一个空的 flush 方法，以免引发警告

# 模拟下载过程（用于进度条更新）
def simulate_download(download_path, log_queue, progress_callback):
    total_size = 100  # 模拟文件的总大小（百分比表示）
    for i in range(total_size + 1):
        time.sleep(0.1)  # 模拟下载进度
        log_queue.put(f"下载进度: {i}%")  # 将进度更新到日志框
        progress_callback(i)  # 更新进度条
    log_queue.put("下载完成！")

# 修改 download_video_async 函数
def download_video_async(platform, url, log_queue, download_path, progress_callback):
    try:
        if platform == 'douyin':
            print("正在下载抖音视频...")
            # 使用 DouyinDownloader 类进行下载
            douyin_downloader = DouyinDownloader(url)
            douyin_downloader.start_download()
            print("抖音视频下载完成！")
        elif platform == 'bilibili':
            print("正在下载哔哩哔哩视频...")
            # 使用 BilibiliDownloader 类进行下载
            bilibili_downloader = BilibiliDownloader(url)
            bilibili_downloader.download_and_merge()
            print("哔哩哔哩视频下载完成！")
        elif platform == 'youtube':
            print("正在下载 YouTube 视频...")
            # 使用 YouTubeDownloader 类进行下载
            youtube_downloader = YouTubeDownloader(url)
            youtube_downloader.download_video()
            print("YouTube 视频下载完成！")
        else:
            print("未知平台，无法下载视频！")

        # 在下载完成后更新进度条
        progress_callback(100)
    except Exception as e:
        print(f"发生错误: {e}")

# 用于更新日志框的函数
def update_log(log_text_widget, log_queue):
    try:
        while True:
            log_message = log_queue.get_nowait()  # 非阻塞地获取队列中的日志消息
            log_text_widget.insert(tk.END, log_message + '\n')  # 添加换行
            log_text_widget.yview(tk.END)  # 自动滚动到最新日志
    except queue.Empty:
        pass

# 更新进度条
def update_progress(progress_bar, progress_value):
    progress_bar['value'] = progress_value
    progress_bar.update_idletasks()

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
            # 创建一个新线程用于下载任务
            download_thread = threading.Thread(target=download_video_async, args=(platform, video_url, log_queue, download_path, update_progress_callback))
            download_thread.start()

    def on_open_folder_button_click():
        # 打开下载文件夹
        download_path = os.path.join(os.getcwd(), 'video')
        if os.path.exists(download_path):
            webbrowser.open(download_path)  # 在文件浏览器中打开下载路径
        else:
            messagebox.showerror("错误", "下载文件夹不存在！")

    def update_progress_callback(progress_value):
        update_progress(progress_bar, progress_value)

    def on_clear_and_paste_button_click():
        # 清空输入框并粘贴剪贴板的内容
        try:
            clipboard_content = window.clipboard_get()  # 获取剪贴板内容
            url_entry.delete(0, tk.END)  # 清空输入框
            url_entry.insert(0, clipboard_content)  # 将剪贴板内容插入输入框
        except tk.TclError:
            messagebox.showerror("错误", "剪贴板为空或无法获取剪贴板内容！")

    # 设置下载路径为项目所在文件夹
    download_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在的目录

    window = tk.Tk()
    window.title("视频下载器     支持平台：B站 抖音 油管 ")
    window.geometry("600x400")

    # 创建一个 Frame 来水平排列输入框和按钮
    top_frame = tk.Frame(window)
    top_frame.pack(pady=10)

    # 输入框
    url_entry = tk.Entry(top_frame, width=50)
    url_entry.pack(side=tk.LEFT)

    # 创建清空并粘贴按钮，放在输入框的右边
    clear_and_paste_button = tk.Button(top_frame, text="一键粘贴", command=on_clear_and_paste_button_click)
    clear_and_paste_button.pack(side=tk.RIGHT, padx=10)

    download_button = tk.Button(window, text="下载视频", command=on_download_button_click)
    download_button.pack(pady=20)

    open_folder_button = tk.Button(window, text="打开文件夹", command=on_open_folder_button_click)
    open_folder_button.pack(pady=5)

    log_text_widget = scrolledtext.ScrolledText(window, width=70, height=10)
    log_text_widget.pack(pady=10)

    # 设置队列用于线程间通信
    log_queue = queue.Queue()

    # 设置 print 重定向
    sys.stdout = PrintRedirector(log_queue)

    # 进度条
    progress_bar = ttk.Progressbar(window, length=300, orient="horizontal", mode="determinate")
    progress_bar.pack(pady=10)

    # 启动一个线程用于更新日志框
    def log_updater():
        update_log(log_text_widget, log_queue)
        window.after(100, log_updater)  # 每100毫秒调用一次更新函数

    log_updater()  # 启动日志更新器

    window.mainloop()

if __name__ == "__main__":
    start_gui()
