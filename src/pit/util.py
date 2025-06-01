import os


def get_file_permission(file_path: str) -> str:
    """ファイルの権限を数字として取得する。ディレクトリなら40000を返す"""
    if os.path.isdir(file_path):
        return "40000"
    # if symlink
    elif os.path.islink(file_path):
        return "120000"  # symlink mode in git
    mode = os.stat(file_path).st_mode
    return str(oct(mode)[2:])
