import hashlib
import subprocess


def calculate_git_hash(file_path):
    """
    Gitのhash-objectの仕組みをPythonで再現してSHA-1ハッシュを計算する。
    """
    with open(file_path, "rb") as f:
        data = f.read()

    # Gitのプレフィックスを追加
    content = f"blob {len(data)}\0".encode() + data

    # SHA-1ハッシュを計算
    return hashlib.sha1(content).hexdigest()


def get_git_hash(file_path):
    """
    実際のgitコマンドを使用してhash-objectの結果を取得する。
    """
    result = subprocess.run(
        ["git", "hash-object", file_path], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()
