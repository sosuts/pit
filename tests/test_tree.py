import os
import subprocess

from pit.objects.blob import Blob
from pit.objects.tree import Tree, TreeEntry


def create_tree_from_directory(directory_path: str) -> Tree:
    """
    指定されたディレクトリからツリーオブジェクトを作成

    :param directory_path: ディレクトリのパス
    :return: 作成されたTreeオブジェクト
    """
    entries = []

    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if subprocess.run(
                ["git", "check-ignore", str(file_name)],
                capture_output=True,
                text=True,
            ).stdout:
                continue
            file_path = os.path.join(root, file_name)
            with open(file_path, "rb") as f:
                file_content = f.read()
            blob = Blob(file_content)
            blob_hash = blob.hash
            mode = "100644"  # 通常のファイルのモード
            relative_path = os.path.relpath(file_path, directory_path)
            entries.append(TreeEntry(mode, relative_path, blob_hash))

        for dir_name in dirs:
            dir = os.path.join(root, dir_name)
            if subprocess.run(
                ["git", "check-ignore", str(dir)],
                capture_output=True,
                text=True,
            ).stdout:
                continue
            dir_path = os.path.join(root, dir_name)
            sub_tree = create_tree_from_directory(dir_path)
            sub_tree_hash = sub_tree.hash
            mode = "040000"  # ディレクトリのモード
            relative_path = os.path.relpath(dir_path, directory_path)
            entries.append(TreeEntry(mode, relative_path, sub_tree_hash))

        break  # os.walkは再帰的にディレクトリを処理するので、最上位のディレクトリのみ処理するためにbreak
    # Treeオブジェクトを作成
    tree = Tree(entries)
    # entryをソート
    tree.entries.sort(key=lambda x: x.name)
    return Tree(entries)


class TestTree:
    def test_src_hash(self):
        """Gitと同じハッシュ値になるか確認する"""

        # assert tree.hash == git_hash.strip()
        subprocess.run(
            ["git", "stash", "push", "-u", "-m", "Temporary stash"], check=True
        )
        try:
            # すべての変更をインデックスに追加
            subprocess.run(["git", "add", "-A"], check=True)

            # Gitのツリーオブジェクトを生成
            git_hash = subprocess.run(
                ["git", "write-tree"],
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()

            # Tree.pyで生成したツリーオブジェクト
            tree = create_tree_from_directory("/home/sosuts/repository/pit")
            assert (
                tree.hash == git_hash
            ), f"Tree hashes do not match! {tree.hash} != {git_hash}"

        finally:
            # インデックスを復元
            subprocess.run(["git", "stash", "pop", "--index"], check=True)
