

"""
    input_video: 在这里放入你的视频文档路径(支持 avi, mp4, mkv, , m4a, mov, flv, wmv, mpeg, webm, ogg"
    model: 在这里放入你想要的whisper模型(tiny, base, small, medium, large, large-v2)
    translate: 是否要翻译字幕文件 (True/False)
    target_lang: 想要翻译的目标语言 (ZH为中文简体, EN为英文)
    auth_key: 翻译软件Deepl API KEY (可以从Deepl注册新账户得到属于自己的API KEY)
    
    详细请见README.md
"""


import subtitleGenerator


def main():

    input_dir = r"C:\Users\leoli\Desktop\videos"
    subtitle_format = "srt"
    model = "medium"
    translation = False
    target_lang = "ZH"
    auth_key = "Deepl-API-KEY"
# ----------------------------------------------------------------
    subtitleGenerator.subtitlesWriter(
        input_dir, subtitle_format, model, translation, target_lang, auth_key)


if __name__ == "__main__":
    main()
