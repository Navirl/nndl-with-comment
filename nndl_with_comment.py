#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import argparse
from convert_json_to_ass import convert_json_to_ass_dir

# 引数パース
parser = argparse.ArgumentParser()
parser.add_argument("url", help="動画のURL")
parser.add_argument("-l", "--location", help="作業ディレクトリ")
parser.add_argument("--only-comments", action="store_true", help="コメントのみダウンロード（動画はスキップ）") 
args = parser.parse_args()

# workdirの決定
if args.location:
    WORKDIR = Path(args.location)
else:
    WORKDIR = Path(__file__).parent

TOOLSPARENT = Path(__file__).parent

YTDLP2JSON = TOOLSPARENT / "yt-dlpjson2nicojson/yt-dlpjson2nicojson.py"
NICOJSON2XML = TOOLSPARENT / "nicojson2xml/nicojson2xml.py"
DANMAKU2ASS = TOOLSPARENT / "nicodanmaku2ass/danmaku2ass.py"

url = args.url.strip()
if not url:
    sys.exit("URL が入力されていません")

ytdlp_cmd = ["yt-dlp", "--write-subs", "--no-warning", "--print", "after_move:filepath"]
if args.only_comments:
    ytdlp_cmd.append("--skip-download")
ytdlp_cmd.append(url)

# yt-dlp 実行（バイトで受け取る）
proc = subprocess.run(
    ["yt-dlp", "--write-subs", "--no-warning", "--print", "after_move:filepath", url],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=WORKDIR,
    text=True,
    errors="replace"
)

output = proc.stdout
print(output)

# 処理を別ファイルの関数に委譲
convert_json_to_ass_dir(output, WORKDIR, YTDLP2JSON, NICOJSON2XML, DANMAKU2ASS)
