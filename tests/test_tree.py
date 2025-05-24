import os
import subprocess
from pathlib import Path

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
            file_path = os.path.join(root, file_name)
            gitignore_result = subprocess.run(
                ["git", "check-ignore", str(file_path)],
                capture_output=True,
                text=True,
            )
            if gitignore_result.stdout:
                continue
            with open(file_path, "rb") as f:
                file_content = f.read()
            blob = Blob(file_content)
            blob_hash = blob.hash
            mode = "100644"  # 通常のファイルのモード
            relative_path = os.path.relpath(file_path, directory_path)
            entries.append(TreeEntry(mode, relative_path, blob_hash))

        for dir_name in dirs:
            dir_ = os.path.join(root, dir_name)
            # dir_の末尾が.gitフォルダは無視
            if dir_.endswith(".git"):
                continue
            gitignore_result = subprocess.run(
                ["git", "check-ignore", str(dir_)],
                capture_output=True,
                text=True,
            )
            if gitignore_result.stdout:
                continue
            dir_path = os.path.join(root, dir_name)
            sub_tree = create_tree_from_directory(dir_path)
            sub_tree_hash = sub_tree.hash
            mode = "40000"  # ディレクトリのモード
            relative_path = os.path.relpath(dir_path, directory_path)
            entries.append(TreeEntry(mode, relative_path, sub_tree_hash))

        break  # os.walkは再帰的にディレクトリを処理するので、最上位のディレクトリのみ処理するためにbreak
    # Treeオブジェクトを作成
    tree = Tree(entries)
    # entryをソート
    tree.entries.sort(key=lambda x: x.name)
    return Tree(entries)


class TestTree:
    def test_src_hash(self, tmp_path):
        """一時的なgitリポジトリでGitと同じハッシュ値になるか確認する"""

        # 一時ディレクトリにリポジトリを作成
        repo_path = Path(tmp_path / "repo")
        (repo_path / "src").mkdir(parents=True, exist_ok=False)
        (repo_path / "src" / "a.txt").write_text("Hello, World!")
        (repo_path / "b.txt").write_text("Hello, World2!\naaaa")
        os.chdir(repo_path)

        # 一時リポジトリのhashを確認するためにGitの初期化とコミットを行う
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "-A"], check=True)

        # Gitのツリーオブジェクトを生成
        git_hash = subprocess.run(
            ["git", "write-tree"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        tree = create_tree_from_directory(str(repo_path))
        assert (
            tree.hash == git_hash
        ), f"Tree hashes do not match! {tree.hash} != {git_hash}"
