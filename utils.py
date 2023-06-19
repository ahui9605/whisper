import ffmpeg
import os
import requests
import json


def is_valid_extension(filename):
    # 检查文件扩展名是否以ffmpeg支持转换MP3
    accepted_extensions = [".avi", ".mp4", ".mkv",
                           ".mov", ".flv", ".wmv", ".mpeg", ".webm", ".ogg", ".m4a"]
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in accepted_extensions


def video_conversion(input_file, output_file):
    # 视频转换为MP3格式
    (
        ffmpeg.input(input_file)
        .output(
            output_file,
            format="mp3",
            acodec="libmp3lame",
            ab="192k",
            fflags="+genpts",
            loglevel="quiet",
        )
        .overwrite_output()
        .run()
    )


def copy_file(source_file, destination_dir):
    # 复制文件到目标目录
    destination_file = os.path.join(
        destination_dir, os.path.basename(source_file))

    with open(source_file, 'rb') as src_file, open(destination_file, 'wb') as dest_file:
        dest_file.write(src_file.read())


def translation_Deepl(input_file, target_lang, auth_key):
    # 使用DeepL进行翻译
    filename = os.path.splitext(os.path.basename(input_file))[0]
    split_name = filename.split('_')
    if "translated" in split_name and target_lang in split_name:
        print(f"已经存在翻译过的字幕文件: {os.path.basename(input_file)}")
        return

    # 设置输出文件路径
    output_file = os.path.join(
        os.path.dirname(input_file),
        f"translated_{target_lang}_{os.path.basename(input_file)}",
    )

    # 设置API端点URL
    url = "https://api-free.deepl.com/v2/translate"

    # 读取输入文件内容
    with open(input_file, "r", encoding="utf-8") as f:
        input_text = f.read()

    # 定义请求载荷
    payload = {"text": input_text,
               "target_lang": target_lang, "source_lang": ""}

    # 发送翻译请求
    response = requests.post(
        url, data=payload, headers={
            "Authorization": f"DeepL-Auth-Key {auth_key}"}
    )

    # 提取翻译后的文本
    translated_text = json.loads(response.text)["translations"][0]["text"]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_text)

    return os.path.basename(input_file)
