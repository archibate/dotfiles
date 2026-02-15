from __future__ import annotations

from pathlib import Path
from typing import Iterable

from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TRCK
from mutagen.mp3 import MP3
from tqdm import tqdm
import argparse
import re


def iter_mp3_files(directory: Path) -> Iterable[Path]:
    return sorted(p for p in directory.glob("*.mp3") if p.is_file())


def parse_track_and_title(mp3_file: Path) -> tuple[int, str]:
    stem = mp3_file.stem
    m = re.match(r"^(\d+)\s+(.+)$", stem)
    if not m:
        raise ValueError(f"Filename does not match '<track> <title>.mp3': {mp3_file.name}")
    return int(m.group(1)), m.group(2)


def write_tags(
    mp3_file: Path,
    cover_bytes: bytes,
    artist: str,
    album: str,
    track_number: int,
    title: str,
) -> None:
    audio = MP3(mp3_file, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()

    # Overwrite existing frames to avoid duplicates
    audio.tags.delall("TPE1")
    audio.tags.delall("TALB")
    audio.tags.delall("APIC")
    audio.tags.delall("TIT2")
    audio.tags.delall("TRCK")

    audio.tags.add(TPE1(encoding=3, text=[artist]))
    audio.tags.add(TALB(encoding=3, text=[album]))
    audio.tags.add(TIT2(encoding=3, text=title))
    audio.tags.add(TRCK(encoding=3, text=str(track_number)))
    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/png",
            type=3,
            desc="Cover",
            data=cover_bytes,
        )
    )
    audio.save(v2_version=3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch tag MP3 files with artist/album/cover.")
    parser.add_argument(
        "--mp3-dir",
        type=Path,
        default=Path("With My Past Soundtrack/Original Soundtrack MP3"),
        help="Directory containing target MP3 files.",
    )
    parser.add_argument(
        "--cover",
        type=Path,
        default=Path("with my past.png"),
        help="PNG cover image file path.",
    )
    parser.add_argument(
        "--artist",
        type=str,
        default="Jiaming Liu",
        help="Artist name to write.",
    )
    parser.add_argument(
        "--album",
        type=str,
        default="With My Past OST",
        help="Album title to write.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    mp3_dir: Path = (args.mp3_dir if args.mp3_dir.is_absolute() else (script_dir / args.mp3_dir)).resolve()
    cover_path: Path = (args.cover if args.cover.is_absolute() else (script_dir / args.cover)).resolve()

    cover_bytes = cover_path.read_bytes()
    files = list(iter_mp3_files(mp3_dir))

    for mp3_path in tqdm(files, desc="Tagging MP3s", unit="file"):
        track_number, title = parse_track_and_title(mp3_path)
        write_tags(mp3_path, cover_bytes, args.artist, args.album, track_number, title)


if __name__ == "__main__":
    main()


