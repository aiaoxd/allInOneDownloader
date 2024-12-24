import os
import yt_dlp as youtube_dl
import sys
import urllib.parse


class YouTubeDownloader:
    def __init__(self, url, download_path=None):
        """
        初始化 YouTubeDownloader 类

        :param url: 需要下载的 YouTube 视频 URL
        :param download_path: 可选，指定下载路径，默认为桌面
        """
        self.url = url
        # self.download_path = download_path or os.path.join(os.path.expanduser('~'), 'Desktop')
        os.makedirs('video', exist_ok=True)
        youtube_video_path = os.path.join('video','youtubeVideo')
        os.makedirs(youtube_video_path,exist_ok=True)
        self.download_path = youtube_video_path or os.path.join(os.path.expanduser('~'), 'Desktop', 'video')
        # 确保下载路径存在
        if not os.path.exists(self.download_path):
            print(f"下载路径不存在: {self.download_path}")
            sys.exit(1)

    def show_progress(self, d):
        """显示下载进度"""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percentage = downloaded / total * 100
            print(f"下载进度: {percentage:.2f}%")

    def load_video_info(self):
        """获取视频信息并展示"""
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'noplaylist': True,
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=False)

                title = info_dict.get('title', '视频')
                formats = info_dict.get('formats', [])
                subtitles = info_dict.get('subtitles', {})

                # 如果没有合适的格式，退出
                if not formats:
                    print("没有找到可下载的视频格式。")
                    sys.exit(1)

                return title, formats, subtitles

        except Exception as e:
            print(f"加载视频信息出错: {e}")
            sys.exit(1)





    def download_video(self):
        """下载视频"""
        # 获取视频信息
        title, formats, subtitles = self.load_video_info()
        ydl_opts = {
            # 'format': 'bestvideo+bestaudio/best',  # 下载最佳视频和音频并合并
            'outtmpl': os.path.join(self.download_path, f"{title}.%(ext)s"),  # 输出文件名模板
            # 'postprocessors': [{  # 使用后处理器将音频和视频合并成 MP4 格式
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mp4',  # 强制转换为 mp4 格式
            # }],
            'progress_hooks': [self.show_progress],  # 显示进度
            'quiet': True,  # 显示更多信息
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])


# 主函数：用于测试
def main():
    # 用法: python 脚本.py <YouTube 视频 URL>
    if len(sys.argv) != 2:
        print("用法: python 脚本.py <YouTube 视频 URL>")
        sys.exit(1)

    url = sys.argv[1]  # 从命令行获取 URL
    downloader = YouTubeDownloader(url)

    # 下载视频
    downloader.download_video()


if __name__ == "__main__":
    main()
