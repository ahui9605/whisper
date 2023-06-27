import subtitleGenerator

"""
    input_video: 在这里放入你的视频文件夹路径 (视频格式支持 avi, mp4, mkv, , m4a, mov, flv, wmv, mpeg, webm, ogg"
    model: 在这里放入你想要的whisper模型来进行字幕转录(tiny, base, small, medium, large, large-v2)
    subtitle_format: 转录后想要的输出格式(支持 vtt, srt, tsv, json , txt。默认为 srt)

    translate: 是否翻译字幕文件 (True/False)
    target_lang: 想要翻译的目标语言 (ZH为中文简体, EN为英文)
    auth_key: 翻译软件Deepl API KEY (可以从Deepl注册新账户得到属于自己的API KEY)
    
    embed_subtitle: 是否烧录字幕(True/False)
    subtitle_background: 是否添加字幕黑色背景提高字幕可读性(True/False)
    subtitle_font: 添加字幕烧录到视频的字体大小(int)
    
    merge_video: 合并音频文件和无音频视频文件(慎用， 部分会自动覆盖 用前备份)
    dir_clearing: 自动清除当前文件夹下mp4和mp3以外的各种媒体文件(慎用，用前备份)
    
    详细请见README.md
"""

options = {
    "input_dir": r"C:\Users\leoli\Desktop\videos",
    "model": "medium",
    "subtitle_format": "srt",
    "translation": False,
    "target_lang": "ZH",
    "auth_key": "Deepl-API-KEY",
    "embed_subtitle": True,
    "subtitle_background": True,
    "subtitle_font": 15,
    "merge_video": True,
    "dir_cleanup": True,
}


def main():
    subtitleGenerator.subtitles_writer(options)


if __name__ == "__main__":
    main()
