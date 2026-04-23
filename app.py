import os
import json
import base64
import gradio as gr

EN_US = os.getenv("LANG") != "zh_CN.UTF-8"
ZH2EN = {
    "收信人": "Recipient",
    "信封正面中心人名": "The recipient centered on front of the envelope",
    "发信人": "Sender",
    "信封背面落款人名": "The sender name on back of the envelope",
    "称呼": "Salutation",
    "信纸左上角称呼": "The salutation in letter's upper left corner",
    "落款": "Signature",
    "信纸右下角落款": "The signature in letter's lower right corner",
    "正文": "Body",
    "信纸上的正文，<br>代表换行，^后的数字代表打字机特效停顿毫秒数": "Body of the letter, <br> represents a line break and the number after ^ represents the number of milliseconds that the typewriter's effects pause",
    "标题": "Title",
    "浏览器标签文本": "Browser tab text",
    "MP3 格式背景音乐": "BGM",
    "状态栏": "Status",
    "下载 JSON 文件": "Download JSON file",
    "复制 JSON 内容": "Copy JSON content",
    "表白信封自定义配置工具": "eLuvLetter JSON Generator",
    "生成": "Generate",
    "清空": "Clear",
    """
    本工具可为你生成自定义版 `content.json` 用于替换你复刻得到的 `eLuvLetter` 仓库内的 `font/content.json`, 其中的背景音乐控件用于上传拆信封时所播放的音频，建议不要太大，请确保音频上传完整后再点击生成按钮。""": """
    This tool can generate your customized `content.json` to replace the `font/content.json` in your forked `eLuvLetter` repository, in which the BGM widget is used to upload the audio played when opening the envelope, it is recommended not to be too large, please make sure the audio is completely uploaded before clicking the Generate button.""",
}

EXAMPLE = (
    "https://www.modelscope.cn/studio/Genius-Society/eluvletter_configurator/resolve/master/example.mp3"
    if EN_US
    else "./example.mp3"
)


def _L(zh_txt: str):
    return ZH2EN[zh_txt] if EN_US else zh_txt


def oversize(file_path: str, size_kb=1024):
    size_bytes = size_kb * 1024
    file_size = os.path.getsize(file_path)
    return file_size >= size_bytes


def toBase64(file_path: str):
    if not file_path:
        file_path = EXAMPLE

    if oversize(file_path):
        return ""

    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()

    base64_encoded = base64.b64encode(audio_data)
    return "data:audio/mpeg;base64," + base64_encoded.decode("utf-8")


def infer(
    recipient: str,
    sender: str,
    salutation: str,
    signature: str,
    body: str,
    title: str,
    bgm: str,
    out_json="./content.json",
):
    status = "Success"
    content = {}
    try:
        if not bgm:
            raise ValueError("请上传背景音乐")

        if os.path.exists(out_json):
            os.remove(out_json)

        content = {
            "recipient": recipient.replace(" ", "&nbsp;"),
            "sender": sender.replace(" ", "&nbsp;"),
            "salutation": salutation.replace(" ", "&nbsp;"),
            "signature": signature.replace(" ", "&nbsp;"),
            "body": body.replace(" ", "&nbsp;"),
            "title": title,
            "bgm": toBase64(bgm),
        }

        if not content["bgm"]:
            raise ValueError("上传的 BGM 过大")

        with open(out_json, "w", encoding="utf-8") as json_file:
            json.dump(
                content,
                json_file,
                ensure_ascii=False,
                indent=4,
            )

        if not os.path.exists(out_json):
            out_json = None
            raise FileExistsError(f"Failed to create {out_json}!")

    except Exception as e:
        status = f"{e}"

    return status, out_json, f"{content}"


if __name__ == "__main__":
    with gr.Blocks() as demo:
        gr.Interface(
            fn=infer,
            inputs=[
                gr.Textbox(
                    label=_L("收信人"),
                    placeholder=_L("信封正面中心人名"),
                ),
                gr.Textbox(
                    label=_L("发信人"),
                    placeholder=_L("信封背面落款人名"),
                ),
                gr.Textbox(
                    label=_L("称呼"),
                    placeholder=_L("信纸左上角称呼"),
                ),
                gr.Textbox(
                    label=_L("落款"),
                    placeholder=_L("信纸右下角落款"),
                ),
                gr.TextArea(
                    label=_L("正文"),
                    placeholder=_L(
                        "信纸上的正文，<br>代表换行，^后的数字代表打字机特效停顿毫秒数"
                    ),
                ),
                gr.Textbox(
                    label=_L("标题"),
                    placeholder=_L("浏览器标签文本"),
                ),
                gr.Audio(
                    label=_L("MP3 格式背景音乐"),
                    type="filepath",
                    format="mp3",
                ),
            ],
            outputs=[
                gr.Textbox(label=_L("状态栏"), buttons=["copy"]),
                gr.File(label=_L("下载 JSON 文件")),
                gr.TextArea(label=_L("复制 JSON 内容"), buttons=["copy"]),
            ],
            examples=[
                [
                    "To  Hiro",
                    "Mika",
                    "弘树",
                    "美嘉",
                    "       如果那天...^600没有^200见到你<br>       我想我^600不会^200那么伤心<br>       那么难过<br>       不会^200泪流满面<br>       但是^600如果^200没有遇见你<br>       我就^200不会了解^600如此高兴<br>       如此^200温柔<br>       如此^200可爱<br>       如此^200温暖<br>       如此^200幸福^200的感觉<br>       ^600现在^600还好吗?<br>       我...^600现在还和天空^200恋爱着",
                    "eLuvLetter",
                    EXAMPLE,
                ]
            ],
            title=_L("表白信封自定义配置工具"),
            submit_btn=_L("生成"),
            clear_btn=_L("清空"),
            flagging_mode="never",
            cache_examples=False,
            description=_L(
                """
    本工具可为你生成自定义版 `content.json` 用于替换你复刻得到的 `eLuvLetter` 仓库内的 `font/content.json`, 其中的背景音乐控件用于上传拆信封时所播放的音频，建议不要太大，请确保音频上传完整后再点击生成按钮。"""
            ),
        )

        gr.HTML(
            """
            <iframe src="//player.bilibili.com/player.html?bvid=BV1hergYREEG&autoplay=0" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" width="100%" style="aspect-ratio: 16 / 9;"></iframe>
            """
        )

    demo.launch(css="#gradio-share-link-button-0 { display: none; }")
