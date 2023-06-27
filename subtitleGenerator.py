import os
import utils
import shutil


def transcribe_and_write_subtitles(
    temp_dir, subtitle_dir, output_format, model, transcribed_audios
):
    for video in os.listdir(subtitle_dir):
        video_name, video_ext = os.path.splitext(video)
        transcribed_audios.setdefault(video_name, set()).add(video_ext)

    # 转录音频并写入字幕
    for mp3_file in os.listdir(temp_dir):
        mp3_name = os.path.splitext(mp3_file)[0]
        if f".{output_format}" in transcribed_audios.get(mp3_name, set()):
            print(f"{output_format}格式的字幕文件已存在: {mp3_file}")
            continue

        print(f"正在转录: {mp3_file}")
        current_file = os.path.join(temp_dir, mp3_file)
        utils.transcribe_audio(current_file, subtitle_dir, output_format, model)

        transcribed_audios.setdefault(mp3_name, set()).add(f".{output_format}")


def burn_in_subtitles(input_dir, transcribed_audios, options):
    subtitle_background = options["subtitle_background"]
    subtitle_font = options["subtitle_font"]
    subtitle_format = options["subtitle_format"]

    for key in transcribed_audios:
        file_basename = f"{key}.mp4"
        if utils.check_embedded_file_exists(input_dir, file_basename, subtitle_format):
            print(f"视频文件已烧录: {file_basename}")
            continue

        file_path = os.path.join(input_dir, f"{key}.mp4")
        if os.path.exists(file_path):
            subtitle_format = next(iter(transcribed_audios[key]))
            new_name = f"embed_{subtitle_format}_{key}.mp4"

            subtitle_file_location = os.path.join(
                input_dir, "subtitles", f"{key}{subtitle_format}"
            )

            utils.burn_in_subtitle(
                input_file=file_path,
                output_file=os.path.join(input_dir, new_name),
                subtitle_file=utils.path_slash_changer(subtitle_file_location),
                subtitle_font=subtitle_font,
                subtitle_background=subtitle_background,
            )
            print(f"烧录字幕成功: {new_name}")
        else:
            print(f"无法烧录字幕: {key}.mp4")


def subtitles_writer(options):
    input_dir = options["input_dir"]
    subtitle_format = options["subtitle_format"]
    model = options["model"]
    translation = options["translation"]
    embed_subtitle = options["embed_subtitle"]
    merge_video = options["merge_video"]
    dir_cleanup = options["dir_cleanup"]

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

    print("正在转换MP3音频...")
    # 将视频转换为MP3格式
    for filename in os.listdir(input_dir):
        mp3_filename = os.path.splitext(filename)[0] + ".mp3"
        if filename.startswith("embed"):
            continue

        if mp3_filename in existing_mp3_files:
            print(f"MP3音频已存在于临时目录中: {filename}")
            continue

        if os.path.splitext(filename)[1] == ".mp3":
            utils.copy_file(os.path.join(input_dir, filename), temp_dir)
            print(f"发现MP3音频: {filename}")
        else:
            utils.video2mp3(filename, input_dir, temp_dir)
            # print(f"视频的MP3音频已存在于临时目录中: {filename}")

    print("-------------------------------------------------------------")

    print("正在转录MP3音频...")
    # 获取已转录视频的列表
    transcribed_audios = {}
    transcribe_and_write_subtitles(
        temp_dir, subtitle_dir, subtitle_format, model, transcribed_audios
    )

    # 如有需要则进行字幕翻译
    if translation:
        print("正在进行字幕翻译...")
        target_lang = options["target_lang"]
        auth_key = options["auth_key"]

        for subtitle in os.listdir(subtitle_dir):
            raw_subtitle = os.path.join(subtitle_dir, subtitle)
            utils.translation_Deepl(raw_subtitle, target_lang, auth_key)

    print("------------------------------------------")

    if merge_video:
        print("合并音频和视频文件")
        utils.merge_audio_video_files(input_dir)

    print("------------------------------------------")

    if embed_subtitle:
        print("正在烧录字幕到视频里...")
        burn_in_subtitles(input_dir, transcribed_audios, options)

    print("------------------------------------------")

    if dir_cleanup:
        utils.filter_files(input_dir)
        for file in os.listdir(input_dir):
            if utils.check_embedded_file_exists(input_dir, file, subtitle_format):
                os.remove(os.path.join(input_dir, file))
        shutil.rmtree(os.path.join(input_dir, "temp"))
    print("已清理部分媒体文件")

    print("------------------------------------------")

    print("转换完成")
