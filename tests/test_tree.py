import os
import random
import subprocess
from pathlib import Path

from pit.objects.tree import Tree


class TestTree:
    def test_dir_hash(self, tmp_path):
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

        tree = Tree.from_directory(str(repo_path))
        assert (
            tree.hash == git_hash
        ), f"Tree hashes do not match! {tree.hash} != {git_hash}"

    def test_symlink_hash(self, tmp_path):
        # 一時ディレクトリにリポジトリを作成
        repo_path = Path(tmp_path / "repo")
        (repo_path / "sym").mkdir(parents=True, exist_ok=False)
        # create a.txt with random unicode characters
        (repo_path / "sym" / "a.txt").write_text(
            "".join([chr(random.randint(0x21, 0x7FF)) for _ in range(100)])
        )
        (repo_path / "sym" / "test_symlink").symlink_to(repo_path / "src" / "a.txt")
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

        tree = Tree.from_directory(str(repo_path))
        for entry in tree.entries:
            print(entry)
        assert (
            tree.hash == git_hash
        ), f"Tree hashes do not match! {tree.hash} != {git_hash}"
