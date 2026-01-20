#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import argparse
from process_video import process_video_files

# 引数パース
parser = argparse.ArgumentParser()
parser.add_argument("url", help="動画のURL")
parser.add_argument("-l", "--location", help="作業ディレクトリ")
args = parser.parse_args()

# workdirの決定
if args.location:
    WORKDIR = Path(args.location)
else:
    WORKDIR = Path(__file__).parent

YTDLP2JSON = WORKDIR / "yt-dlpjson2nicojson/yt-dlpjson2nicojson.py"
NICOJSON2XML = WORKDIR / "nicojson2xml/nicojson2xml.py"
DANMAKU2ASS = WORKDIR / "nicodanmaku2ass/danmaku2ass.py"

url = args.url.strip()
if not url:
    sys.exit("URL が入力されていません")

# yt-dlp 実行（バイトで受け取る）
proc = subprocess.run(
    ["yt-dlp", "--no-warning", "--print", "after_move:filepath", url],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=WORKDIR,
)

# Windows(cp932) でデコード
output = proc.stdout.decode("cp932", errors="replace")
print(output)

# 処理を別ファイルの関数に委譲
process_video_files(output, WORKDIR, YTDLP2JSON, NICOJSON2XML, DANMAKU2ASS)
