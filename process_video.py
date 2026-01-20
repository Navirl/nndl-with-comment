from pathlib import Path
import subprocess
import sys
import argparse


def process_video_files(output, workdir, ytdlp2json, nicojson2xml, danmaku2ass):
    """yt-dlpの出力から動画ファイルを処理する"""
    for line in output.splitlines():
        if not line.strip():
            continue
        
        video_file = Path(line.strip())
        dir_path = video_file.parent
        name_only = video_file.stem
        
        comments_json = dir_path / f"{name_only}.comments.json"
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
    
    # .comments.json ファイルを再帰的に検索
    comment_files = folder_path.rglob("*.comments.json")
    
    # output形式に変換（.comments.jsonを除いたベース名）
    output_lines = []
    for comment_file in comment_files:
        # .comments.json を除いたベース名を取得
        base_name = comment_file.name.replace(".comments.json", "")
        # 元のビデオファイル名を再構築（拡張子は仮に.mp4とする）
        video_path = comment_file.parent / f"{base_name}.mp4"
        output_lines.append(str(video_path))
    
    if not output_lines:
        print(f"警告: {folder_path} に .comments.json ファイルが見つかりませんでした")
        sys.exit(0)
    
    output = "\n".join(output_lines)
    print(f"見つかったファイル:\n{output}\n")
    
    # 処理実行
    process_video_files(output, WORKDIR, YTDLP2JSON, NICOJSON2XML, DANMAKU2ASS)
