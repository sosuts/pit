import hashlib
import subprocess
import zlib
from pathlib import Path

from pit import util
from pit.objects.blob import Blob


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
        elif self.mode == "120000":
            return "symlink"
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
        # docstring
        """
        Treeのエントリをバイト列に変換
        :return: Treeのエントリをバイト列に変換したもの
        """
        return b"".join(entry.to_bytes() for entry in self.entries)

    @property
    def hash(self) -> str:
        return hashlib.sha1(self.content).hexdigest()

    def save(self, file_path: str | None = None, base_path: str = ".") -> None:
        """
        Treeデータを指定されたファイルに保存し、参照するblobやtreeも保存
        """
        for entry in self.entries:
            if entry.type() == "tree":
                # サブツリーの絶対パスを解決
                sub_tree_path = Path(base_path) / entry.name
                Tree.from_directory(str(sub_tree_path)).save(
                    base_path=str(sub_tree_path)
                )
            elif entry.type() == "blob" or entry.type() == "symlink":
                # 必要ならここで保存処理を追加
                pass

        # 自身のtreeオブジェクトを保存
        if file_path is None:
            file_path = f".pit/objects/{self.hash[0:2]}/{self.hash[2:]}"
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        else:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(zlib.compress(self.content))

    def _find_entry_path(self, name: str) -> str:
        # Treeのディレクトリパスからエントリ名でパスを返す（必要に応じて実装）
        return name

    @staticmethod
    def from_directory(directory: str) -> "Tree":
        """
        指定されたディレクトリからツリーオブジェクトを作成

        :param directory: ディレクトリのパス
        :return: 作成されたTreeオブジェクト
        """

        entries = []
        dir_path = Path(directory)

        for entry in dir_path.iterdir():
            if entry.name == ".git":
                continue
            # gitignoreチェック
            gitignore_result = subprocess.run(
                ["git", "check-ignore", str(entry.resolve())],
                capture_output=True,
                text=True,
            )
            if gitignore_result.stdout:
                continue
            mode = util.get_file_permission(str(entry))

            if entry.is_symlink():
                # シンボリックリンクのリンク先パスをblobとして保存
                link_target = entry.readlink()
                blob = Blob(str(link_target).encode("utf-8"))
                tree_entry = TreeEntry(mode, entry.name, blob.hash)
                entries.append(tree_entry)
            elif entry.is_file():
                with entry.open("rb") as f:
                    file_content = f.read()
                tree_entry = TreeEntry(mode, entry.name, Blob(file_content).hash)
                entries.append(tree_entry)
            elif entry.is_dir():
                entries.append(
                    TreeEntry(
                        mode,
                        entry.name,
                        Tree.from_directory(str(entry)).hash,
                    )
                )
            else:
                raise ValueError(f"Unsupported entry type: {entry}")

        # 名前順でソート
        entries = sorted(entries, key=lambda x: x.name)
        return Tree(entries)
