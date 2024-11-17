import hashlib
from functools import lru_cache
from string import Template


class Blob:
    PREFIX = Template("blob $length\0")

    def __init__(self, data: str | bytes) -> None:
        """
        Blobオブジェクトの初期化

        :param data: バイナリまたは文字列のデータ
        """
        if isinstance(data, str):
            # Gitではデータがバイナリで保持される
            self.data = data.encode()
        elif isinstance(data, bytes):
            self.data = data
        else:
            raise ValueError("Data must be a string or bytes.")

    @property
    @lru_cache
    def hash(self) -> str:
        """
        BlobのSHA-1ハッシュを計算。
        """
        # fmt: off
        prefix = self.PREFIX.substitute(length=len(self.data)).encode()
        sha1 = hashlib.sha1(prefix + self.data)
        # cliは出力の末尾に改行コードを含めることが多いらしい
        return sha1.hexdigest() + "\n"

    def save(self, file_path: str) -> None:
        """
        Blobデータを指定されたファイルに保存。
        """
        with open(file_path, "wb") as f:
            f.write(self.data)

    @staticmethod
    def load_from_file(file_path: str) -> "Blob":
        """
        ファイルからBlobオブジェクトを作成。

        :param file_path: 読み込むファイルのパス
        :return: Blobオブジェクト
        """
        with open(file_path, "rb") as f:
            data = f.read()
        return Blob(data)
