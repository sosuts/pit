import hashlib
from string import Template


class Blob:
    def __init__(self, data: str | bytes) -> None:
        """Initialize a Blob object.

        Args:
            data (str | bytes): The content of the blob.

        Raises:
            ValueError: If the data is not str or bytes.
        """
        if isinstance(data, str):
            self.__data = data.encode()
        elif isinstance(data, bytes):
            self.__data = data
        else:
            raise ValueError("data must be str or bytes.")

    @property
    def template(self) -> Template:
        """
        Blobオブジェクトのテンプレート文字列を返す。
        """
        return Template("blob $length\0$data")

    @property
    def content(self) -> str:
        """
        Blobオブジェクトの内容を返す。
        """
        return self.template.substitute(length=len(self.data), data=self.data.decode())

    @property
    def hash(self) -> str:
        """
        BlobのSHA-1ハッシュを計算。
        """
        content = self.content.encode()
        sha1 = hashlib.sha1(content).hexdigest()
        return sha1

    def save(self, file_path: str) -> None:
        """Blobオブジェクトをファイルに保存。

        Args:
            file_path (str): 保存するファイルのパス
        """
        content = self.content.encode()
        with open(file_path, "wb") as f:
            f.write(content)

    @staticmethod
    def load_from_file(file_path: str) -> "Blob":
        """
        ファイルからBlobオブジェクトを作成。

        :param file_path: 読み込むファイルのパス
        :return: Blobオブジェクト
        """
        with open(file_path, "rb") as f:
            data = f.read()
            if not data.startswith(b"blob "):
                raise ValueError("Invalid blob object.")
            data = data[data.index(b"\0") + 1 :]
        return Blob(data)

    def __eq__(self, other: object) -> bool:
        """
        Blobオブジェクト同士を比較。
        """
        if not isinstance(other, Blob):
            return NotImplemented
        return self.hash == other.hash

    def __repr__(self) -> str:
        """
        Blobオブジェクトの文字列表現を返す。
        """
        return f"Blob(hash={self.hash.strip()}, size={len(self.__data)})"

    @property
    def size(self) -> int:
        """
        Blobデータのサイズを返す。
        """
        return len(self.__data)

    @property
    def data(self) -> bytes:
        """
        Blobデータを返す。
        """
        return self.__data

    @property
    def type(self) -> str:
        """
        Blobのタイプを返す。
        """
        return "blob"
