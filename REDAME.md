# Whisper 语音识别

Whisper 是一个通用的语音识别模型，是在一个大型的不同音频数据集上训练出来的。它是一个多任务模型，可以进行多语言语音识别、语音翻译和语言识别。这个 Whisper 可以用来转录音频文件，生成字幕，并翻译字幕。Whisper 的输入可以是一个音频或视频文件。输出可以是一个文本文件或一个字幕文件。

## 更新

- 部分路径无需再进行填写， 该代码运行会自动检测指定路径下的 MP3 音频和部分支持的视频文件并转换成 MP3 支持音频， 只需填写一个路径即可。

- 运行后的音频文件会放到一个代码生成后的**temp**文档里
- 运行后的字幕文件会放到一个代码生成后的**subtitles**文档里
- 增加烧录字幕功能， 可以自动把转录后的字幕内容烧录到视频里
- 增加合并纯音频文件和无音频视频文件并导出 MP4 格式(慎用，部分文件会覆盖)
- 自动删除在**input_dir**文件夹里 MP4 和 MP3 以外的各种媒体文件和 **temp** 文件夹(慎用，部分文件会覆盖)

- 因部分来自 Whisper 的最新源码有个别变动，代码里的内容大部分已经重构和重写

## 部署环境

需要 Python 3.9 以上 和[PyTorch 1.10.1](https://pytorch.org/get-started/locally/)

需要 [Nvidia Cuda](https://developer.nvidia.com/cuda-11-8-0-download-archive)

安装 Whisper

```sh
pip install -U openai-whisper
```

```sh
pip install git+https://github.com/openai/whisper.git
```

如要将 Whisper 更新到该仓库的最新版本：

```sh
pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
```

安装 ffmpeg

```sh
pip install ffmpeg-python
```

安装其他可选的 python 库

```sh
pip install deepl
```

## 可用的模型和语言

Whisper 模型提供了不同规模，每个模型都有自己的速度和精度的平衡。模型大小从 "tiny "到 "large-v2 "不等，随着模型大小的增加，内存需求和相对速度也在增加, Whisper 的转录性能因所使用的语言而异。

支持的语言识别： [Whisper Tokenizer](https://github.com/openai/whisper/blob/b5851c6c40e753606765ac45b85b298e3ae9e00d/whisper/tokenizer.py#L10-L110)

| 模型     | 所需的 VRAM | 相对速度 |
| -------- | ----------- | -------- |
| tiny     | ~ 1GB       | ~ 32x    |
| base     | ~ 1GB       | ~ 16x    |
| small    | ~ 2GB       | ~ 6x     |
| medium   | ~ 5GB       | ~2x      |
| large    | ~ 10GB      | 1x       |
| large-v2 | ~ 10GB+     | 1x       |

## 使用方法

需要在 [main.py](https://github.com/ahui9605/whisper/blob/bf20861062727987f18a176c1c8def083ae016c3/main.py#L25-L36) 文件中的各个变量中自行配置各种选项，打开该文件并按以下格式添加选项：

| Options             | Type         | Description                                                                                                                                                                                             |
| ------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| input_dir           | 文件路径     | 输入视频文件或目录的路径                                                                                                                                                                                |
| ~~output_mp3~~      | ~~文件路径~~ | ~~转换后的 mp3 音频文件的输出目录的路径~~                                                                                                                                                               |
| ~~output_subtitle~~ | ~~文件路径~~ | ~~生成的字幕文件的输出目录的路径~~                                                                                                                                                                      |
| model               | String       | 音频转写所使用的 Whisper 模型。默认为 medium                                                                                                                                                            |
| subtitle_format     | String       | 生成的字幕文件的格式，支持 vtt, srt, tsv, json , txt。默认为 srt                                                                                                                                        |
| translation         | Boolean      | 是否翻译字幕文件。默认为 False                                                                                                                                                                          |
| target_lang         | String       | 字幕翻译的目标语言，[DeepL 语言代码](<https://www.deepl.com/docs-api/translate-text#:~:text=and%20translate%20it.-,target_lang,ZH%20%2D%20Chinese%20(simplified),-split_sentences>)。默认为简体中文: ZH |
| auth_key            | String       | 调用 Deepl API 翻译工具，需要 API 密钥。                                                                                                                                                                |
| embed_subtitle      | Boolean      | 是否烧录字幕(True/False)                                                                                                                                                                                |
| subtitle_background | Boolean      | 添加字幕黑色背景(提高视频不同背景下的可读性)                                                                                                                                                            |
| subtitle_font       | Int          | 添加字幕烧录到视频的字体大小                                                                                                                                                                            |
| merge_video         | Boolean      | 合并音频文件和无音频视频文件(慎用)                                                                                                                                                                      |
| dir_cleanup         | Boolean      | 自动清除 mp4 和 mp3 以外的各种媒体文件(慎用)                                                                                                                                                            |

## 翻译工具 API

当前使用的翻译工具是 DeepL。要使用其他翻译工具，请替换以下函数调用。

```sh
if translation:
    for subtitle in os.listdir(subtitle_dir):
        raw_subtitle = os.path.join(subtitle_dir, subtitle)

        #可替换函数
        utils.translation_Deepl(raw_subtitle, target_lang, auth_key)
```

例如要使用百度翻译 API，请参考其文档并创建一个适当的函数，确保新的函数接受部分相同的参数，最后输出翻译后的文件到指定文件夹。

例如：

```sh
    translation_Baidu(raw_subtitle, source_lag, target_lang, appid, api_key)
```

**"raw_subtitle" 是一个字幕文件路径，需要使用 "with open xxx as xxx" 的方式逐行读取并提取每一句子进行翻译，最后再重新写入。**

## 更多用法

更多的用法可以在 Whisper 的[transcripy.py](https://github.com/openai/whisper/blob/b5851c6c40e753606765ac45b85b298e3ae9e00d/whisper/transcribe.py#L370-L405)中通过命令行进行高阶 whisper 音频转录
