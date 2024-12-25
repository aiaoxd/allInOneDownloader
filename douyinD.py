def get_modalid_from_share_link(self):
        """从分享链接中提取 modal_id"""

        # 匹配分享视频链接 (例如 https://www.douyin.com/video/{modal_id})
        video_pattern = r'https://www\.douyin\.com/video/(\d+)'

        # 匹配带有 modal_id 参数的用户链接
        user_pattern = r'https://www\.douyin\.com/user/.+?modal_id=(\d+)'

        # 匹配带有 modal_id 参数的 discover 链接
        discover_pattern = r'https://www\.douyin\.com/discover\?modal_id=(\d+)'

        # 匹配带有 modal_id 参数的搜索链接（新增）
        search_pattern = r'https://www\.douyin\.com/search/.+?modal_id=(\d+)'

        # 尝试匹配分享视频链接中的 modal_id
        match = re.search(video_pattern, self.share_link)
        if match:
            modal_id = match.group(1)
            print(f"Extracted modal_id from video link: {modal_id}")
            return modal_id

        # 尝试匹配用户链接中的 modal_id
        match = re.search(user_pattern, self.share_link)
        if match:
            modal_id = match.group(1)
            print(f"Extracted modal_id from user link: {modal_id}")
            return modal_id

        # 尝试匹配 discover 链接中的 modal_id
        match = re.search(discover_pattern, self.share_link)
        if match:
            modal_id = match.group(1)
            print(f"Extracted modal_id from discover link: {modal_id}")
            return modal_id

        # 尝试匹配搜索链接中的 modal_id
        match = re.search(search_pattern, self.share_link)
        if match:
            modal_id = match.group(1)
            print(f"Extracted modal_id from search link: {modal_id}")
            return modal_id

        # 如果没有找到，继续处理分享链接
        pattern = r'https://v\.douyin\.com/[a-zA-Z0-9]+/?'
        try:
            # 提取分享链接中的 URL 部分
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
