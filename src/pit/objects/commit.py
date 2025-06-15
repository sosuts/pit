import hashlib
from datetime import datetime
from string import Template


class Commit:
    def __init__(self, tree, parents, author, committer, message):
        self.tree = tree
        self.parents = parents
        self.author = author
        self.committer = committer
        self.message = message

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
        timestamp = int(datetime.now().timestamp())
        timezone = datetime.now().astimezone().strftime("%z")
        parents_str = "\n".join(self.parents) if self.parents else ""
        return (
            f"tree {self.tree}\n"
            f"parent {parents_str}\n"
            f"author {self.author} {timestamp} {timezone}\n"
            f"committer {self.committer} {timestamp} {timezone}\n\n"
            f"{self.message}\n"
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
        return (
            f"tree {self.tree}\n"
            f"parent {self.parents}\n"
            f"author {self.author}\n"
            f"committer {self.committer}\n"
            f"\n"
            f"{self.message}\n"
        )
