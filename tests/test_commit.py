import os
import subprocess
from datetime import datetime
from pathlib import Path

from pit.objects.commit import Commit
from pit.objects.tree import Tree


class TestCommit:
    GIT_AUTHOR_DATE = int(datetime(2025, 12, 1, 12, 34, 56).timestamp())
    GIT_COMMITTER_DATE = int(datetime(2025, 12, 1, 12, 34, 56).timestamp())

    def test_tree_hash_when_time_is_fixed(self, tmp_path):
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
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = str(self.GIT_AUTHOR_DATE)
        env["GIT_COMMITTER_DATE"] = str(self.GIT_COMMITTER_DATE)
        subprocess.run(
            ["git", "commit", "-m", "test commit"],
            capture_output=True,
            check=True,
            env=env,
        )

        # ツリーのハッシュを取得
        git_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        # Pitのツリーを作成
        tree_ = Tree.from_directory(str(repo_path))
        # self.GIT_AUTHOR_DATEとself.GIT_COMMITTER_DATEをintに変換して渡す
        commit = Commit(
            tree=tree_,
            author="sosuts <sosuke.utsunomiya@gmail.com>",
            committer="sosuts <sosuke.utsunomiya@gmail.com>",
            message="test commit",
            timestamp=self.GIT_AUTHOR_DATE,
            timezone=datetime.fromtimestamp(self.GIT_AUTHOR_DATE)
            .astimezone()
            .strftime("%z"),
        )
        assert commit.hash == git_hash, (
            f"Commit hashes do not match! {commit.hash} != {git_hash}"
        )
