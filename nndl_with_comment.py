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
parser.add_argument("-s", "--skip-download", action="store_true", help="コメントのみダウンロード（動画はスキップ）")
parser.add_argument("-f", "--format", help="yt-dlpに渡す品質（フォーマット）指定 例: bestvideo+bestaudio, 22")
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

# ニコニコのコメント(comments)とYouTubeのライブチャット(live_chat)を取得
# 非ASCII文字(é等)が化けないよう出力はUTF-8に固定
ytdlp_cmd = ["yt-dlp", "--write-subs", "--sub-langs", "comments,live_chat", "--no-warning", "--encoding", "utf-8"]
if args.skip_download:
    # 動画をダウンロードしないとafter_moveは発火しないため、after_videoでファイル名を出力
    ytdlp_cmd.extend(["--skip-download", "--print", "after_video:%(filename)s"])
else:
    ytdlp_cmd.extend(["--print", "after_move:filepath"])
if args.format:
    ytdlp_cmd.extend(["-f", args.format])
ytdlp_cmd.append(url)

# yt-dlp 実行（バイトで受け取る）
proc = subprocess.run(
    ytdlp_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=WORKDIR,
    text=True,
    encoding="utf-8",
    errors="replace"
)

output = proc.stdout
print(output)

# 処理を別ファイルの関数に委譲
convert_json_to_ass_dir(output, WORKDIR, YTDLP2JSON, NICOJSON2XML, DANMAKU2ASS)
