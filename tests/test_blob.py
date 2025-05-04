import subprocess

import pytest

from pit.objects.blob import Blob


class TestBlob:
    def test_blob_encode(self):
        """
        Blobオブジェクトの初期化をテスト
        データがバイナリに変換されているか確認
        """
        data = "Hello, Git!"
        blob = Blob(data)
        assert blob.data == data.encode()

    def test_blob_save_load(self, tmp_path):
        """
        Blobオブジェクトの保存をテスト
        """
        data = "Hello, Git!"
        blob = Blob(data)
        file_path = tmp_path / "blob"
        blob.save(file_path)
        # ファイルが保存されているか確認
        assert file_path.exists()
        # ファイルの内容が正しいか確認
        with open(file_path, "rb") as f:
            blob = Blob.load_from_file(file_path)
            truth = f"blob {len(data)}\0{data}"
            assert f.read() == truth.encode()

    @pytest.mark.parametrize(
        "data",
        [
            "test content",
            "Multiple\nLines\n",
            "適当な日本語",
            "複数行の\n日本語",
            "!(dfs)[@],.,!#$%&x//'",
        ],
    )
    def test_hash(self, data):
        """Gitと同じハッシュ値になるか確認する"""
        blob = Blob(data)
        git_hash = subprocess.run(
            ["git", "hash-object", "--stdin"],
            input=data,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert blob.hash == git_hash.strip()
