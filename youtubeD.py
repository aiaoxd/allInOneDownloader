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
        self.download_path = download_path or os.path.join(os.path.expanduser('~'), 'Desktop')

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

    def select_best_format(self, formats):
        """筛选并选择filesize最大的视频格式"""
        # 筛选出同时包含 'filesize' 和 'height'，且 'filesize' 不是 None，'acodec' 不是 None 的格式
        valid_formats = [
            fmt for fmt in formats
            if 'filesize' in fmt and fmt['filesize'] is not None
               and 'height' in fmt
               and 'audio_channels' in fmt and fmt['audio_channels'] is not None
        ]

        # 如果没有合适的格式，退出
        if not valid_formats:
            print("没有找到合适的视频格式。")
            sys.exit(1)

        # 根据 'filesize' 排序，选择最大的视频格式
        best_format = max(valid_formats, key=lambda x: x['filesize'])
        return best_format

    def download_video(self):
        """下载视频"""
        # 获取视频信息
        title, formats, subtitles = self.load_video_info()

        # 选择最清晰的视频格式
        selected_format = self.select_best_format(formats)
        print(selected_format)
        print(selected_format["resolution"])

        if 'height' in selected_format and 'filesize' in selected_format:
            quality_text = f"{selected_format['height']}p - {selected_format['filesize'] / 1024 / 1024:.2f} MB"
        elif 'filesize' in selected_format:  # 可能是音频
            quality_text = f"音频 - {selected_format['filesize'] / 1024 / 1024:.2f} MB"
        else:
            print("选择的格式不包含有效的质量信息")
            return

        print(f"正在下载 {quality_text} 格式...")

        # 使用 youtube-dl 进行下载操作，确保选中合适的格式。
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # 下载最佳视频和音频并合并
            'outtmpl': os.path.join(self.download_path, f"{title}.%(ext)s"),  # 输出文件名模板
            'postprocessors': [{  # 使用后处理器将音频和视频合并成 MP4 格式
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # 强制转换为 mp4 格式
            }],
            'progress_hooks': [self.show_progress],  # 显示进度
            'quiet': False,  # 显示更多信息
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
