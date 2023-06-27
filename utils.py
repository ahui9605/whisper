import ffmpeg
import os
import subprocess
import requests
import json
import whisper
from whisper import utils as whisper_utils
from difflib import SequenceMatcher


def get_basename(full_path):
    return os.path.splitext(os.path.basename(full_path))[0]


def copy_file(source_file, destination_dir):
    # 复制文件到目标目录
    destination_file = os.path.join(destination_dir, os.path.basename(source_file))

    with open(source_file, "rb") as src_file, open(destination_file, "wb") as dest_file:
        dest_file.write(src_file.read())


def path_slash_changer(path):
    # 替换路径分隔符和冒号
    # 如: subtitle_file = r"c\\:\\\\Users\\\\leoli\\\\Desktop\\\\whisper\\\\test_new_captions.srt"
    original_path = path
    new_path = original_path.replace("\\", "\\\\\\\\")  # 替换反斜杠
    new_path = new_path.replace(":", "\\\:")  # 替换冒号

    return new_path


def search_codec(codec_name):
    # 查找硬件加速支持技术
    command = ["ffmpeg", "-loglevel", "quiet", "-codecs"]
    output = subprocess.check_output(command).decode("utf-8")
    codecs = output.split("\n")
    for line in codecs:
        if codec_name in line:
            return True
    return False


def is_valid_extension(filename):
    # 检查文件扩展名是否支持转换
    accepted_extensions = [
        ".avi",
        ".mp4",
        ".mkv",
        ".mov",
        ".flv",
        ".wmv",
        ".mpeg",
        ".webm",
        ".ogg",
        ".m4a",
        ".m4s",
    ]
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in accepted_extensions


def video2mp3(file, input_dir, temp_dir):
    # Convert video to MP3 format
    if is_valid_extension(file):
        input_file = os.path.join(input_dir, file)
        temp_file = os.path.join(temp_dir, os.path.splitext(file)[0] + ".mp3")
        return video_conversion(input_file, temp_file)

    return False


def video_conversion(input_file, output_file):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-vn",
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        "-f",
        "mp3",
        output_file,
    ]

    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print(f"音频转换成功：{os.path.basename(input_file)}")
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode("utf-8").strip().split("\n")
        last_line = error_output[-1]
        print(f"{os.path.basename(input_file)} 错误发生: {last_line} ")
    # 转换MP3格式的音频文件
    # (ffmpeg.input(input_file).output(output_file,format="mp3",acodec="libmp3lame",ab="192k",fflags="+genpts",loglevel="quiet",).overwrite_output().run())


def is_empty_video(file):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-select_streams",
        "v",
        "-count_packets",
        "-of",
        "json",
        file,
    ]

    try:
        output = subprocess.check_output(command, stderr=subprocess.PIPE)
        output = output.decode("utf-8")
        data = json.loads(output)

        # Check if the "streams" field is empty
        if "streams" not in data or len(data["streams"]) == 0:
            return True
        else:
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error executing ffprobe: {e}")
        return False


def check_embedded_file_exists(folder_path, original_file_name, subtitle_format):
    original_file_path = os.path.join(folder_path, original_file_name)
    embedded_file_prefix = f"embed_.{subtitle_format}_"
    embedded_file_path = os.path.join(
        folder_path, embedded_file_prefix + original_file_name
    )

    return os.path.exists(original_file_path) and os.path.exists(embedded_file_path)
    # # 用法示例
    # folder_path = r"C:\Users\leoli\Desktop\videos"
    # original_file_name = "test.mp4"
    # subtitle_format = "srt"
    # result = check_embedded_file_exists(folder_path, original_file_name, subtitle_format)
    # print(result)


def filter_files(folder_path):
    allowed_extensions = [".mp3", ".mp4"]
    files_to_delete = [
        filename
        for filename in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, filename))  # 只处理文件，不删除文件夹
        and os.path.splitext(filename)[1].lower() not in allowed_extensions
    ]

    for filename in files_to_delete:
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)

    # # 用法示例
    # folder_path = r"C:\Users\leoli\Desktop\videos"
    # filter_files(folder_path)

    # dir = r"C:\Users\leoli\Desktop\videosx"
    # subtitle_format = "srt"

    # filter_files(dir)
    # for file in os.listdir(dir):
    #     if check_embedded_file_exists(dir, file, subtitle_format):
    #         os.remove(os.path.join(dir, file))
    # shutil.rmtree(os.path.join(dir, "temp"))


def transcribe_audio(mp3_file, output_dir, output_format, model):
    # 调用Whisper库进行转录音频
    model = whisper.load_model(model)
    result = model.transcribe(mp3_file)
    # print= result["text"]

    options = {
        "max_line_width": 500,
        "max_line_count": 20,
        "highlight_words": False,
    }

    # 根据输出格式从Whisper获取适当的写入器
    writer = whisper_utils.get_writer(output_format, output_dir)

    # 创建输出文件路径
    audio_basename = os.path.basename(mp3_file)
    audio_basename = os.path.splitext(audio_basename)[0]
    output_path = os.path.join(output_dir, audio_basename + "." + writer.extension)

    writer(result, output_path, options)


def burn_in_subtitle(
    input_file, output_file, subtitle_file, subtitle_font, subtitle_background
):
    # 烧录字幕
    codec = "libx264"  # Default to CPU decoder
    if search_codec("h264_nvenc"):
        codec = "h264_nvenc"  # Use CUDA decoder if supported

    vf = f"subtitles={subtitle_file}:force_style='FontSize={subtitle_font}'"
    if subtitle_background:
        vf = f"subtitles={subtitle_file}:force_style='BackColour=`&H80000000,BorderStyle=4,OutlineColour=`&H80000000,Outline=1,Shadow=0'"

    ffmpeg.input(input_file).output(
        output_file,
        vf=vf,
        **{"c:v": codec, "preset": "slow"},
    ).run(quiet=True, overwrite_output=True)

    # input_file = r"c:\Users\leoli\Desktop\whisper\test.mp4"
    # output_file = r"c:\Users\leoli\Desktop\whisper\test_1.mp4"
    # font_size = 12

    # 正常刻录字幕
    # # FFmpeg command to burn captions
    # ffmpeg.input(input_file).output(
    #     output_file, vf=f"subtitles={subtitle_file}").run()

    # 添加字幕背景，黑色背景
    # ffmpeg.input(input_file).output(
    #     output_file, vf=f"subtitles={subtitle_file}:force_style='BackColour=`&H80000000,BorderStyle=4,OutlineColour=`&H80000000,Outline=1,Shadow=0'"
    # ).run()

    # 调整字体大小
    #     ffmpeg.input(input_file).output(
    #         output_file, vf=f"subtitles={subtitle_file}:force_style='FontSize={subtitle_font},BackColour=&H80000000,BorderStyle=4,OutlineColour=&H80000000,Outline=1,Shadow=0'").run()


def translation_Deepl(input_file, target_lang, auth_key):
    # 使用DeepL进行翻译字幕文件
    filename = get_basename(input_file)
    split_name = filename.split("_")
    if "translated" in split_name and target_lang in split_name:
        print(f"已经存在翻译过的字幕文件: {os.path.basename(input_file)}")
        return

    output_file = os.path.join(
        os.path.dirname(input_file),
        f"translated_{target_lang}_{os.path.basename(input_file)}",
    )
    url = "https://api-free.deepl.com/v2/translate"

    with open(input_file, "r", encoding="utf-8") as f:
        input_text = f.read()
    payload = {"text": input_text, "target_lang": target_lang, "source_lang": ""}
    response = requests.post(
        url, data=payload, headers={"Authorization": f"DeepL-Auth-Key {auth_key}"}
    )
    # 提取翻译后的文本
    translated_text = json.loads(response.text)["translations"][0]["text"]
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_text)
    return os.path.basename(input_file)


def merge_audio_video_files(input_dir):
    def get_media_info(file_path):
        cmd = "ffprobe -v quiet -print_format json -show_streams"
        args = cmd.split()
        args.append(file_path)
        ffprobe_output = subprocess.check_output(args).decode("utf-8")
        ffprobe_output = json.loads(ffprobe_output)

        audio_streams = [
            x for x in ffprobe_output["streams"] if x["codec_type"] == "audio"
        ]
        video_streams = [
            x for x in ffprobe_output["streams"] if x["codec_type"] == "video"
        ]

        return len(audio_streams), len(video_streams)

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    # 获取目录中的所有m4s文件
    files = [f for f in os.listdir(input_dir) if f.endswith(".m4s")]

    audio_files = []
    video_files = []

    # 检查每个文件
    for file in files:
        file_path = os.path.join(input_dir, file)
        audio_streams, video_streams = get_media_info(file_path)
        if audio_streams > 0:
            audio_files.append(file_path)
        if video_streams > 0:
            video_files.append(file_path)

    # 合并匹配的音频和视频文件
    for audio_file in audio_files:
        audio_name = get_basename(audio_file)
        best_match_ratio = 0
        best_match_video_file = None

        for video_file in video_files:
            video_name = get_basename(video_file)
            match_ratio = similar(audio_name, video_name)

            if match_ratio > best_match_ratio:
                best_match_ratio = match_ratio
                best_match_video_file = video_file

        if best_match_video_file is not None:
            output_file = os.path.join(input_dir, audio_name + ".mp4")
            cmd = f'ffmpeg -y -loglevel quiet -i "{audio_file}" -i "{best_match_video_file}" -c:v copy -c:a copy "{output_file}"'
            subprocess.call(cmd, shell=True)
            print(f"合并成功: {os.path.basename(output_file)}")
        else:
            print(f"找不到匹配的视频文件用于音频文件: {os.path.basename(audio_file)}")
    # # 示例用法
    # input_directory = r"C:\Users\leoli\Desktop\videos\test"
    # merge_audio_video_files(input_directory)
