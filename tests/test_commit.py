import os
import subprocess
from pathlib import Path

from pit.objects.commit import Commit
from pit.objects.tree import Tree


class TestCommit:
    def test_dir_hash(self, tmp_path, freezer):
        freezer.move_to("2025-12-01 12:34:56")
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
        subprocess.run(
            ["git", "commit", "-m", "test commit"],
            capture_output=True,
            check=True,
        )
        # get commit hash
        git_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        tree_ = Tree.from_directory(str(repo_path))
        commit = Commit(
            tree=tree_,
            parents=[git_hash],
            author="sosuts <sosuke.utsunomiya@gmail.com>",
            committer="sosuts <sosuke.utsunomiya@gmail.com>",
            message="test commit",
        )
        print(commit.content)
