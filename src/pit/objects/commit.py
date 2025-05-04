import hashlib
from datetime import datetime
from string import Template

from pit.objects.tree import Tree


class Commit:
    def __init__(
        self, tree: Tree, parents: list[str] | None, author: str, message: str
    ) -> None:
        """
        Commitオブジェクトの初期化

        :param tree: コミットが指すツリーオブジェクト
        :param parents: 親コミットのハッシュリスト
        :param author: コミットの作者情報
        :param message: コミットメッセージ
        """
        self.tree = tree
        self.parents = parents if parents else []
        self.author = author
        self.message = message
        self.timestamp = datetime.now()

    @property
    def template(self) -> Template:
        return Template(
            "tree $tree\n"
            "$parents"
            "author $author $timestamp +0000\n"
            "committer $author $timestamp +0000\n"
            "\n"
            "$message\n"
        )

    @property
    def content(self) -> str:
        return self.template.substitute(
            tree=self.tree.hash,
            parents="\n".join([f"parent {parent}" for parent in self.parents]),
            author=self.author,
            timestamp=int(self.timestamp.timestamp()),
            message=self.message,
        )

    @property
    def hash(self) -> str:
        """
        CommitのSHA-1ハッシュを計算
        """
        data = self.to_bytes()
        sha1 = hashlib.sha1(data).hexdigest()
        return sha1

    def to_bytes(self) -> bytes:
        """
        Commitオブジェクトをバイナリ形式に変換

        :return: バイナリ形式のCommit
        """
        data = self.template.substitute(
            tree=self.tree.hash,
            parents="\n".join([f"parent {parent}" for parent in self.parents]),
            author=self.author,
            timestamp=int(self.timestamp.timestamp()),
            message=self.message,
        )
        return f"commit {len(data)}\0{data}".encode()

    def save(self, file_path: str) -> None:
        """
        Commitデータを指定されたファイルに保存

        :param file_path: 保存するファイルのパス
        """
        data = self.to_bytes()
        with open(file_path, "wb") as f:
            f.write(data)

    @staticmethod
    def load_from_file(file_path: str) -> "Commit":
        """
        ファイルからCommitオブジェクトを作成

        :param file_path: 読み込むファイルのパス
        :return: Commitオブジェクト
        """
        with open(file_path, "rb") as f:
            data = f.read()
        if not data.startswith(b"commit "):
            raise ValueError("Invalid commit object.")
        data = data[data.index(b"\0") + 1 :].decode()
        lines = data.split("\n")
        tree_hash = lines[0].split(" ")[1]
        parents = [line.split(" ")[1] for line in lines if line.startswith("parent")]
        author = lines[len(parents) + 1].split(" ")[1]
        message = "\n".join(lines[len(parents) + 4 :]).strip()
        tree = Tree.load_from_file(f".pit/objects/{tree_hash}")
        return Commit(tree, parents, author, message)

    def __repr__(self) -> str:
        """
        Commitオブジェクトの文字列表現を返す
        """
        return f"Commit(hash={self.hash}, tree={self.tree.hash}, parents={self.parents}, author={self.author}, message={self.message})"


commit = Commit(Tree(), [], "author", "message")
print(commit)
