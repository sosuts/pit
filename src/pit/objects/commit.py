import hashlib
from datetime import datetime
from string import Template

from pit.objects.tree import Tree


class Commit:
    def __init__(
        self,
        tree: Tree,
        parents: list[str] | None = None,
        author: str = "",
        committer: str = "",
        message: str = "",
        timestamp: int | None = None,
        timezone: str | None = None,
    ):
        self.tree: Tree = tree
        self.parents = parents
        self.author = author
        self.committer = committer
        self.message = message
        if timestamp is not None:
            self.__timestamp = timestamp
        else:
            self.__timestamp = int(datetime.now().timestamp())
        if timezone is not None:
            self.__timezone = timezone
        else:
            self.__timezone = datetime.now().astimezone().strftime("%z")

    def template(self) -> Template:
        """
        Commitオブジェクトのテンプレート文字列を返す。
        """
        return Template("commit $length\0$content")

    @property
    def content(self) -> str:
        """
        Commitオブジェクトの内容を返す。
        """
        parents_str = "\n".join(self.parents) if self.parents else ""
        return (
            f"tree {self.tree.hash}\n"
            + (f"parent {parents_str}\n" if self.parents else "")
            + f"author {self.author} {self.__timestamp} {self.__timezone}\n"
            + f"committer {self.committer} {self.__timestamp} {self.__timezone}\n\n"
            + f"{self.message}\n"
        )

    @property
    def hash(self) -> str:
        """
        BlobのSHA-1ハッシュを計算。
        """
        content = self.content
        content = f"commit {len(content)}\0" + content
        # print(f"content: {content}")
        return hashlib.sha1(content.encode()).hexdigest()

    def __str__(self):
        """
        Gitと同じようにコミットオブジェクトの文字列表現を返す。
        """
        if self.parents:
            parents_str = "\n".join(f"parent {p}" for p in self.parents)
        else:
            parents_str = ""
        return (
            f"tree {self.tree.hash}\n"
            + parents_str
            + f"author {self.author} {self.__timestamp} {self.__timezone}\n"
            + f"committer {self.committer} {self.__timestamp} {self.__timezone} \n"
            f"\n"
            f"{self.message}\n"
        )

    def __repr__(self) -> str:
        return self.__str__()
