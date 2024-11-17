import hashlib
from string import Template


class Commit:
    # テンプレート文字列をクラス変数として定義
    TEMPLATE = Template(
        "tree $tree\n"
        "$parents"
        "author $author $timestamp\n"
        "committer $author $timestamp\n\n"
        "$message\n"
    )

    def __init__(self, tree, parents, author, message, timestamp=None):
        self.tree = tree  # ツリーオブジェクトのハッシュ
        self.parents = parents  # 親コミットのハッシュリスト
        self.author = author  # 作成者情報 "名前 <メール>"
        self.message = message  # コミットメッセージ
        self.timestamp = timestamp  # タイムスタンプ (Unix形式)
        self.hash = None  # 計算されたハッシュを格納する

    def compute_hash(self):
        # 親コミットをテンプレート用に整形
        parents_str = "".join(f"parent {parent}\n" for parent in self.parents)

        # テンプレートに変数を代入
        content = self.TEMPLATE.substitute(
            tree=self.tree,
            parents=parents_str,
            author=self.author,
            timestamp=self.timestamp,
            message=self.message,
        )

        # プレフィックス付きの内容を生成
        full_content = f"commit {len(content)}\0{content}"

        # SHA-1ハッシュを計算
        self.hash = hashlib.sha1(full_content.encode()).hexdigest()
        return self.hash
