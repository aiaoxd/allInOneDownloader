import json
import os
import re
import requests
from urllib.parse import unquote
from tqdm import tqdm


class DouyinDownloader:
    def __init__(self, share_link, download_folder='doyinVideo'):
        """
        初始化 DouyinDownloader 类

        :param share_link: 抖音视频分享链接
        :param download_folder: 下载保存的文件夹，默认是 'doyinVideo'
        """
        self.share_link = share_link
        self.download_folder = download_folder
        self.headers = {
            'Referer': 'https://www.douyin.com/',
            'cookie': 'douyin.com; device_web_cpu_core=10; device_web_memory_size=8; __ac_nonce=06760391f00b9b51264ae; __ac_signature=_02B4Z6wo00f019a5ceAAAIDAhEZR-X3jjWfWmXVAAJLXd4; ttwid=1%7C7MTKBSMsP4eOv9h5NAh8p0E-NYIud09ftNmB0mjLpWc%7C1734359327%7C8794abeabbd47447e1f56e5abc726be089f2a0344d6343b5f75f23e7b0f0028f; UIFID_TEMP=0de8750d2b188f4235dbfd208e44abbb976428f0720eb983255afefa45d39c0c6532e1d4768dd8587bf919f866ff1396912bcb2af71efee56a14a2a9f37b74010d0a0413795262f6d4afe02a032ac7ab; s_v_web_id=verify_m4r4ribr_c7krmY1z_WoeI_43po_ATpO_I4o8U1bex2D7; hevc_supported=true; home_can_add_dy_2_desktop=%220%22; dy_swidth=2560; dy_sheight=1440; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2560%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A10%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; strategyABtestKey=%221734359328.577%22; csrf_session_id=2f53aed9aa6974e83aa9a1014180c3a4; fpk1=U2FsdGVkX1/IpBh0qdmlKAVhGyYHgur4/VtL9AReZoeSxadXn4juKvsakahRGqjxOPytHWspYoBogyhS/V6QSw==; fpk2=0845b309c7b9b957afd9ecf775a4c21f; passport_csrf_token=d80e0c5b2fa2328219856be5ba7e671e; passport_csrf_token_default=d80e0c5b2fa2328219856be5ba7e671e; odin_tt=3c891091d2eb0f4718c1d5645bc4a0017032d4d5aa989decb729e9da2ad570918cbe5e9133dc6b145fa8c758de98efe32ff1f81aa0d611e838cc73ab08ef7d3f6adf66ab4d10e8372ddd628f94f16b8e; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; bd_ticket_guard_client_web_domain=2; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; UIFID=0de8750d2b188f4235dbfd208e44abbb976428f0720eb983255afefa45d39c0c6532e1d4768dd8587bf919f866ff139655a3c2b735923234f371c699560c657923fd3d6c5b63ab7bb9b83423b6cb4787e2ce66a7fbc4ecb24c8570f520fe6de068bbb95115023c0c6c1b6ee31b49fb7e3996fb8349f43a3fd8b7a61cd9e18e8fe65eb6a7c13de4c0960d84e344b644725db3eb2fa6b7caf821de1b50527979f2; is_dash_user=1; biz_trace_id=b57a241f; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTEo2R0lDalVoWW1XcHpGOFdrN0Vrc0dXcCtaUzNKY1g4NGNGY2k0TTl1TEowNjdUb21mbFU5aDdvWVBGamhNRWNRQWtKdnN1MnM3RmpTWnlJQXpHMjA9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; download_guide=%221%2F20241216%2F0%22; sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f276364697660272927666d776a68605a607d71606b766c6a6b5a7666776c7571273f275e58272927666a6b766a69605a696c6061273f27636469766027292762696a6764695a7364776c6467696076273f275e5827292771273f273d33323131333c3036313632342778; bit_env=RiOY4jzzpxZoVCl6zdVSVhVRjdwHRTxqcqWdqMBZLPGjMdB4Tax1kAELHNTVAAh72KuhumewE4Lq6f0-VJ2UpJrkrhSxoPw9LUb3zQrq1OSwbeSPHkRlRgRQvO89sItdGUyq1oFr0XyRCnMYG87KSeWyc4x0czGR0o50hTDoDLG5rJVoRcdQOLvjiAegsqyytKF59sPX_QM9qffK2SqYsg0hCggURc_AI6kguDDE5DvG0bnyz1utw4z1eEnIoLrkGDqzqBZj4dOAr0BVU6ofbsS-pOQ2u2PM1dLP9FlBVBlVaqYVgHJeSLsR5k76BRTddUjTb4zEilVIEwAMJWGN4I1BxVt6fC9B5tBQpuT0lj3n3eKXCKXZsd8FrEs5_pbfDsxV-e_WMiXI2ff4qxiTC0U73sfo9OpicKICtZjdq8qsHxJuu6wVR36zvXeL2Wch5C6MzprNvkivv0l8nbh2mSgy1nabZr3dmU6NcR-Bg3Q3xTWUlR9aAUmpopC-cNuXjgLpT-Lw1AYGilSUnCvosth1Gfypq-b0MpgmdSDgTrQ%3D; gulu_source_res=eyJwX2luIjoiMDhjOGQ3ZTJiODQyNjZkZWI5Y2VkMGJiODNlNmY1ZWY0ZjMyNTE2ZmYyZjAzNDMzZjI0OWU1Y2Q1NTczNTk5NyJ9; passport_auth_mix_state=hp9bc3dgb1tm5wd8p82zawus27g0e3ue; IsDouyinActive=false',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

        # 确保下载文件夹存在
        os.makedirs(self.download_folder, exist_ok=True)

    def sanitize_filename(self, title):
        """替换非法字符（例如 Windows 系统中的非法字符）"""
        sanitized_title = re.sub(r'[<>:"/\\|?*]', '_', title)  # 将非法字符替换为 '_'
        sanitized_title = sanitized_title.strip()  # 去除两端的空格
        return sanitized_title

    def download_video(self, url, title):
        """下载视频"""
        response = requests.get(url, headers=self.headers, stream=True)
        print(f"HTTP Status Code: {response.status_code}")

        if response.status_code == 200:
            # 获取文件的总大小
            total_size = int(response.headers.get('Content-Length', 0))
            video_path = os.path.join(self.download_folder, f"{self.sanitize_filename(title)}.mp4")

            # 保存视频文件
            with open(video_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))  # 更新进度条
            print(f"Video {video_path} downloaded successfully.")
        else:
            print("Failed to retrieve the video.")

    def get_video_url(self, url):
        """获取视频播放地址"""
        response = requests.get(url, headers=self.headers)
        content = re.findall('</div><script id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)
        content = unquote(content[0])
        content = json.loads(content)
        part_url = content["app"]["videoDetail"]["video"]["bitRateList"][0]['playAddr'][0]['src']
        title = content["app"]["videoDetail"]["desc"]
        print(f"Title: {title}")
        print("Video URL: https://" + part_url)

        return "https:" + part_url, title

    def get_modalid_from_share_link(self):
        """从分享链接中提取 modal_id"""
        pattern = r'https://v\.douyin\.com/[a-zA-Z0-9]+/?'

        # 提取分享链接中的 URL 部分
        try:
            url = re.findall(pattern, self.share_link)[0]
        except Exception as e:
            print('Invalid URL')
            return None

        print(f"Extracted URL: {url}")

        # 重试机制，最多重试5次
        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                # 使用线程来进行请求
                response = self.make_request(url)

                # 检查是否成功获取最终重定向 URL
                if response.url:
                    print(f"Final Redirect URL: {response.url}")
                    print(response.url)
                    # 提取 video modal_id
                    pattern = r'https://www\.douyin\.com/video/(\d+)'
                    match = re.search(pattern, response.url)

                    if match:
                        modal_id = match.group(1)
                        print(f"Extracted modal_id: {modal_id}")
                        return modal_id
                    else:
                        print("No modal_id found in final URL.")
                        retries += 1
                        time.sleep(2)  # 等待 2 秒再尝试
                        print(f"Retrying... ({retries}/{max_retries})")
                else:
                    print("Invalid response URL. Retrying...")
                    retries += 1
                    time.sleep(2)  # 等待 2 秒再尝试
                    print(f"Retrying... ({retries}/{max_retries})")

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Request error: {e}. Retrying... ({retries}/{max_retries})")
                time.sleep(2)  # 等待 2 秒再尝试

        print("Max retries reached. Could not retrieve the modal_id.")
        return None

    def make_request(self, url):
        """处理请求的函数，包含超时设置"""
        try:
            response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=10)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            raise
    def start_download(self):
        """主函数，开始下载视频"""
        modal_id = self.get_modalid_from_share_link()
        if not modal_id:
            print("Invalid share link.")
        else:
            url = f'https://www.douyin.com/user/MS4wLjABAAAAf7i8sK5OxbSctQ45rmH2dDIFYNPmlqHRtnGucIQSRSGuQUiiYEoxdc2QpBIu5XmS?from_tab_name=main&modal_id={modal_id}'
            play_url, title = self.get_video_url(url)
            self.download_video(play_url, title)


# 示例调用方法
if __name__ == '__main__':
    # 通过命令行传入分享链接
    import argparse

    parser = argparse.ArgumentParser(description="Douyin Video Downloader")
    parser.add_argument('share_link', type=str, help='Douyin video share link')
    args = parser.parse_args()

    downloader = DouyinDownloader(f'''{args.share_link}''')
    downloader.start_download()
