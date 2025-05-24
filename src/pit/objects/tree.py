import hashlib


class TreeEntry:
    def __init__(self, mode: str, name: str, hash: str) -> None:
        """
        TreeEntryオブジェクトの初期化

        :param mode: ファイルのパーミッション
        :param name: ファイルやディレクトリの名前
        :param hash: 対応するblobまたはtreeオブジェクトのSHA-1ハッシュ
        """
        self.mode = mode
        self.name = name
        self.hash = hash

    def to_bytes(self) -> bytes:
        return f"{self.mode} {self.name}\0".encode() + bytes.fromhex(self.hash)

    @staticmethod
    def from_bytes(data: bytes) -> "TreeEntry":
        """
        バイナリデータからTreeEntryオブジェクトを作成

        :param data: バイナリデータ
        :return: TreeEntryオブジェクト
        """
        parts = data.split(b"\0", 1)
        mode_name = parts[0].decode()
        hash = parts[1].hex()
        mode, name = mode_name.split(" ", 1)
        return TreeEntry(mode, name, hash)

    def type(self) -> str:
        """
        TreeEntryがディレクトリかどうかを返す

        :return: ディレクトリの場合True
        """
        if self.mode == "40000":
            return "tree"
        else:
            return "blob"

    def __repr__(self) -> str:
        """
        TreeEntryオブジェクトの文字列表現を返す
        """
        _hash = self.hash.strip()
        # modeを6桁に左から0埋め
        return f"{self.mode.zfill(6)} {self.type()} {_hash}\t{self.name}"


class Tree:
    def __init__(self, entries: list[TreeEntry] | None = None) -> None:
        self.entries = entries if entries else []

    def add_entry(self, entry: TreeEntry) -> None:
        """
        Treeに新しいエントリを追加

        :param entry: 追加するTreeEntryオブジェクト
        """
        self.entries.append(entry)

    @property
    def content(self) -> bytes:
        # テンプレートを使わず、直接バイト列で返す
        return f"tree {len(self.data)}\0".encode() + self.data

    @property
    def data(self) -> bytes:
        return b"".join(entry.to_bytes() for entry in self.entries)

    @property
    def hash(self) -> str:
        return hashlib.sha1(self.content).hexdigest()

    def save(self, file_path: str) -> None:
        """
        Treeデータを指定されたファイルに保存

        :param file_path: 保存するファイルのパス
        """
        with open(file_path, "wb") as f:
            f.write(self.content)
