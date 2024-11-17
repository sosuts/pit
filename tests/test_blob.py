import subprocess

import pytest

from pit.objects.blob import Blob


class TestBlob:
    def test_data(self):
        """
        Blobオブジェクトの初期化をテスト
        """
        data = "Hello, Git!"
        blob = Blob(data)
        # データがバイナリに変換されているか確認
        assert blob.data == data.encode()

        data = "Hello, Git!"
        blob = Blob(data)
        git_hash = subprocess.run(
            ["git", "hash-object", "--stdin"],
            # inputは文字列らしい
            input=data,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert blob.hash == git_hash

    @pytest.mark.parametrize(
        "data", ["Hello, Git!", "Multiple\nLines\n", "適当な日本語", "複数行の\n日本語"]
    )
    def hash(self):
        """
        Blobオブジェクトのハッシュ計算をテスト
        """
        data = "Hello, Git!"
        blob = Blob(data)
        # 実際のgitのhashと結果を比較する
        git_hash = subprocess.run(
            ["git", "hash-object", "--stdin"],
            input=data,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        assert blob.hash == git_hash
