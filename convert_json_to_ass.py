from pathlib import Path
import subprocess
import sys
import argparse

# yt-dlpが出力するコメントファイルの接尾辞（ニコニコ / YouTube live chat）
COMMENT_SUFFIXES = (".comments.json", ".live_chat.json")


def find_comments_file(dir_path, name_only):
    """動画に対応するコメントファイルを探す（見つからなければNone）"""
    for suffix in COMMENT_SUFFIXES:
        candidate = dir_path / f"{name_only}{suffix}"
        if candidate.exists():
            return candidate
    return None


def convert_json_to_ass_dir(output, workdir, ytdlp2json, nicojson2xml, danmaku2ass):
    """yt-dlpの出力から動画ファイルを処理する"""
    for line in output.splitlines():
        if not line.strip():
            continue
        
        video_file = Path(line.strip())
        dir_path = video_file.parent
        name_only = video_file.stem
        
        comments_json = find_comments_file(dir_path, name_only)
        if comments_json is None:
            print(f"警告: {name_only} のコメントファイルが見つかりません。スキップします")
            continue
        comments_conv_json = dir_path / f"{name_only}.commentsconv.json"
        comments_xml = dir_path / f"{name_only}.commentsconv.xml"
        ass_file = dir_path / f"{name_only}.ass"
        
        subprocess.run(
            ["python3", str(ytdlp2json), str(comments_json), str(comments_conv_json)],
            check=True,
            cwd=workdir,
        )
        subprocess.run(
            ["python3", str(nicojson2xml), str(comments_conv_json)],
            check=True,
            cwd=workdir,
        )
        subprocess.run(
            ["python3", str(danmaku2ass), "-o", str(ass_file), "-a", "0.8", str(comments_xml)],
            check=True,
            cwd=workdir,
        )


if __name__ == "__main__":
    # 単体実行時の処理
    parser = argparse.ArgumentParser(description="コメントファイルを変換する")
    parser.add_argument("folder", help="検索するフォルダパス")
    parser.add_argument("-l", "--location", help="作業ディレクトリ")
    args = parser.parse_args()
    
    folder_path = Path(args.folder)
    if not folder_path.exists() or not folder_path.is_dir():
        sys.exit(f"エラー: {folder_path} はディレクトリではありません")
    
    # workdirの決定
    if args.location:
        WORKDIR = Path(args.location)
    else:
        WORKDIR = Path(__file__).parent
    
    YTDLP2JSON = WORKDIR / "yt-dlpjson2nicojson/yt-dlpjson2nicojson.py"
    NICOJSON2XML = WORKDIR / "nicojson2xml/nicojson2xml.py"
    DANMAKU2ASS = WORKDIR / "nicodanmaku2ass/danmaku2ass.py"
    
    # .comments.json / .live_chat.json ファイルを再帰的に検索
    output_lines = []
    for suffix in COMMENT_SUFFIXES:
        for comment_file in folder_path.rglob(f"*{suffix}"):
            # 接尾辞を除いたベース名を取得
            base_name = comment_file.name[: -len(suffix)]
            # 元のビデオファイル名を再構築（拡張子は仮に.mp4とする）
            video_path = str(comment_file.parent / f"{base_name}.mp4")
            # 両方存在する場合の重複を防ぐ
            if video_path not in output_lines:
                output_lines.append(video_path)
    
    if not output_lines:
        print(f"警告: {folder_path} に .comments.json / .live_chat.json ファイルが見つかりませんでした")
        sys.exit(0)
    
    output = "\n".join(output_lines)
    print(f"見つかったファイル:\n{output}\n")
    
    # 処理実行
    convert_json_to_ass_dir(output, WORKDIR, YTDLP2JSON, NICOJSON2XML, DANMAKU2ASS)
