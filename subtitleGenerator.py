import whisper
from whisper import utils as whisper_utils
import os
import utils


def transcribe_audio(mp3_file, output_dir, output_format, model):
    # 调用Whisper库进行转录音频
    model = whisper.load_model(model)
    result = model.transcribe(mp3_file)
    # print= result["text"]

    options = {
        "max_line_width": 1500,
        "max_line_count": 200,
        "highlight_words": False,
    }

    # 根据输出格式获取适当的写入器
    writer = whisper_utils.get_writer(output_format, output_dir)

    # 创建输出文件路径
    audio_basename = os.path.basename(mp3_file)
    audio_basename = os.path.splitext(audio_basename)[0]
    output_path = os.path.join(
        output_dir, audio_basename + "." + writer.extension)

    writer(result, output_path, options)


# 将视频转换为MP3格式
def video2mp3(file, input_dir, temp_dir):
    if utils.is_valid_extension(file):
        input_file = os.path.join(input_dir, file)
        temp_dir = os.path.join(
            temp_dir, os.path.splitext(file)[0] + ".mp3"
        )
        utils.video_conversion(input_file, temp_dir)
        print(f"音频转换成功：{file}")
        return True
    return False


def subtitlesWriter(input_dir, output_format, model, translation, target_lang, auth_key):
    # 创建临时目录和字幕目录
    temp_dir = os.path.join(input_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    subtitle_dir = os.path.join(input_dir, "subtitles")
    os.makedirs(subtitle_dir, exist_ok=True)

    # 获取临时目录中现有的MP3文件列表
    existing_mp3_files = set()
    for filename in os.listdir(temp_dir):
        if os.path.splitext(filename)[1] == ".mp3":
            existing_mp3_files.add(filename)

    # 将视频转换为MP3格式
    for filename in os.listdir(input_dir):
        mp3_filename = os.path.splitext(filename)[0] + ".mp3"
        if os.path.splitext(filename)[1] == ".mp3":
            if mp3_filename not in existing_mp3_files:
                utils.copy_file(os.path.join(input_dir, filename), temp_dir)
                print(f"发现MP3音频：{filename}")
            else:
                print(f"MP3音频已存在于临时目录中：{filename}")
        else:
            if mp3_filename not in existing_mp3_files:
                video2mp3(filename, input_dir, temp_dir)
            else:
                print(f"视频的MP3音频已存在于临时目录中：{filename}")

    print("-------------------------------------------------------------")
    transcribed_audios = {}

    # 获取已转录视频的列表
    for video in os.listdir(subtitle_dir):
        video_name, video_ext = os.path.splitext(video)
        if video_name not in transcribed_audios:
            transcribed_audios[video_name] = set()
        transcribed_audios[video_name].add(video_ext)

    # 转录音频并写入字幕
    for mp3_file in os.listdir(temp_dir):
        mp3_name = os.path.splitext(mp3_file)[0]
        # 检查以避免重复转录
        if f".{output_format}" not in transcribed_audios.get(mp3_name, set()):
            print(f"正在转录：{mp3_file}")
            current_file = os.path.join(temp_dir, mp3_file)
            transcribe_audio(current_file, subtitle_dir, output_format, model)
            if mp3_name not in transcribed_audios:
                transcribed_audios[mp3_name] = set()
            transcribed_audios[mp3_name].add(f".{output_format}")
        else:
            print(f"{output_format}格式的字幕文件已存在：{mp3_file}")

    # 如有需要，进行字幕翻译
    if translation:
        for subtitle in os.listdir(subtitle_dir):
            raw_subtitle = os.path.join(subtitle_dir, subtitle)
            utils.translation_Deepl(raw_subtitle, target_lang, auth_key)

    print("转换完成")
