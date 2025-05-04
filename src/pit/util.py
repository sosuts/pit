import os


def get_file_permission(file_path):
    """ファイルの権限を数字として取得する。ディレクトリなら40000を返す"""
    if os.path.isdir(file_path):
        return 40000
    mode = os.stat(file_path).st_mode
    return int(oct(mode)[2:])
