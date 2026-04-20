import time
import argparse
import requests
from modelscope import HubApi


def restart_studio(
    token: str,
    repo="Genius-Society/insects",
    endpoint="https://www.modelscope.cn",
    hold=5,
):
    repo_page = f"{endpoint}/studios/{repo}"
    status_api = f"{endpoint}/api/v1/studio/{repo}/status"
    reboot_api = f"{endpoint}/api/v1/studio/{repo}/reset_restart"
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537",
            "Cookie": token2ck(token),
        }
        response = requests.put(reboot_api, headers=header)
        response.raise_for_status()
        time.sleep(hold)
        while (
            requests.get(status_api, headers=header).json()["Data"]["Status"]
            != "Running"
        ):
            requests.get(repo_page, headers=header)
            time.sleep(hold)

    except requests.exceptions.Timeout as e:
        print(f"激活创空间 {repo} 失败: {e}, 重试中...")
        restart_studio(repo)

    except Exception as e:
        print(f"激活创空间 {repo} 失败: {e}")


def token2ck(token: str) -> str:
    api = HubApi()
    api.login(token)
    ck_dict = api.session.cookies.get_dict()
    cookies = [f"{k}={v}" for k, v in ck_dict.items()]
    return "; ".join(cookies)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset restart ModelScope studio")
    parser.add_argument("--token", required=True, help="Your ModelScope Access Token")
    args = parser.parse_args()
    restart_studio(args.token)
