import hashlib
import struct
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class IndexEntry:
    BINARY_FORMAT: ClassVar[str] = (
        ">"
        "I"  # 1. Creation time in seconds
        "I"  # 2. Creation time in nanoseconds
        "I"  # 3. Modification time in seconds
        "I"  # 4. Modification time in nanoseconds
        "I"  # 5. Device ID
        "I"  # 6. Inode number
        "I"  # 7. Mode
        "I"  # 8. User ID
        "I"  # 9. Group ID
        "I"  # 10. File size
        "20s"  # 11. Object ID (SHA-1 hash)
        "H"  # 12. Flags (name length + stage + extended flag)
    )
    ctime: int  # Creation time in seconds
    ctime_ns: int  # Creation time in nanoseconds
    mtime: int  # Modification time in seconds
    mtime_ns: int  # Modification time in nanoseconds
    dev: int  # Device ID I
    ino: int  # Inode number I
    mode: int  # Mode I
    uid: int  # User ID I
    gid: int  # Group ID I
    size: int  # File size I
    object_hash: str  # Object ID as a hex string
    flags: int  # Flags I
    name: str

    def to_bytes(self) -> bytes:
        name_bytes = self.name.encode("utf-8")
        name_length = min(len(name_bytes), 0xFFF)
        flags = (self.flags & 0xF000) | name_length

        entry_data = (
            struct.pack(
                self.BINARY_FORMAT,
                self.ctime,
                self.ctime_ns,
                self.mtime,
                self.mtime_ns,
                self.dev,
                self.ino,
                self.mode,
                self.uid,
                self.gid,
                self.size,
                bytes.fromhex(self.object_hash),
                flags,
            )
            + name_bytes
            + b"\0"
        )

        padding_length = (8 - (len(entry_data) % 8)) % 8
        return entry_data + b"\0" * padding_length

    @classmethod
    def from_bytes(cls, data: bytes, offset: int = 0) -> tuple["IndexEntry", int]:
        if len(data) < offset + struct.calcsize(cls.BINARY_FORMAT):
            raise ValueError("Insufficient data for index entry")
        entry_data = struct.unpack_from(cls.BINARY_FORMAT, data, offset)
        (
            ctime,  # 1. Creation time in seconds
            ctime_ns,  # 2. Creation time in nanoseconds
            mtime,  # 3. Modification time in seconds
            mtime_ns,  # 4. Modification time in nanoseconds
            dev,  # 5. Device ID I
            ino,  # 6. Inode number I
            mode,  # 7. Mode I
            uid,  # 8. User ID I
            gid,  # 9. Group ID I
            size,  # 10. File size I
            hash_bytes,  # 11. Object ID
            flags,
        ) = entry_data
        hash_bytes = hash_bytes.hex()

        # assume_valid_flag: int = flags & (1 << 16)
        extended_flag: int = flags & (1 << 15)
        # stage: int = flags & (3 << 14)
        if extended_flag != 0:
            raise ValueError(
                f"Pit only supports basic index entries, not extended ones: {flags:#x}"
            )
        name_length = flags & 0xFFF
        name_start = offset + struct.calcsize(cls.BINARY_FORMAT)
        name_end = name_start + name_length

        if len(data) < name_end:
            raise ValueError("Insufficient data for entry name")

        # Find null terminator after name
        null_pos = data.find(b"\0", name_start)
        if null_pos == -1:
            raise ValueError("Missing null terminator for entry name")

        name = data[name_start:null_pos].decode("utf-8")

        # Calculate padding to align to 8-byte boundary
        entry_size = (
            struct.calcsize(IndexEntry.BINARY_FORMAT) + len(name.encode("utf-8")) + 1
        )
        padding_length = (8 - (entry_size % 8)) % 8
        padding_end = null_pos + 1 + padding_length

        entry = IndexEntry(
            ctime,
            ctime_ns,
            mtime,
            mtime_ns,
            dev,
            ino,
            mode,
            uid,
            gid,
            size,
            hash_bytes,
            flags,
            name,
        )
        return entry, padding_end

    @property
    def object_type(self) -> int:
        """modeからobject_typeを取得する。
        modeの上位4ビットを取得
        """
        return (self.mode >> (len(format(self.mode, "b")) - 4)) & 0b1111

    @property
    def unix_permission(self) -> int:
        """
        modeからunix_permissionを取得する。
        unix_permissionは、modeの下位9ビット
        """
        return self.mode & 0x1FF


class Index:
    SIGNATURE = b"DIRC"
    VERSION = 2
    HEADER_SIZE = 12  # Size of the header in bytes

    def __init__(self) -> None:
        self.entries: list[IndexEntry] = []

    @classmethod
    def load(cls, data: bytes) -> "Index":
        if len(data) < 32:
            raise ValueError("Index file too small")

        signature, version, entry_count = struct.unpack(
            ">4sII", data[: cls.HEADER_SIZE]
        )
        if signature != cls.SIGNATURE:
            # rと!がないとバイナリb''でprintされる
            raise ValueError(f"Invalid index signature: {signature!r}")
        if version != cls.VERSION:
            raise ValueError(f"Unsupported index version: {version}")

        stored_checksum = data[-20:]
        content_data = data[:-20]
        calculated_checksum = hashlib.sha1(content_data).digest()

        if stored_checksum != calculated_checksum:
            raise ValueError("Index checksum mismatch")

        index = cls()
        offset = cls.HEADER_SIZE

        for _ in range(entry_count):
            entry, offset = IndexEntry.from_bytes(data, offset)
            index.entries.append(entry)

        return index
