#!/usr/bin/env python3
"""puzzles_data.js を koburin-generator の問題データから再生成する。

koburin-generator (~/puzzle20261005) は問題を次の2か所に保持している。
  - verify/puzzles/*.json                         既知問題（001_sample_13x13 など。id はファイル名）
  - generated_puzzles/13x13/*/detail/puzzle.json  生成問題（id はディレクトリ名）
ここでは上記を SOURCE_GLOBS の順に読み、表示に不要な解答フィールド（solution 等）を落として
puzzles_data.js に書き出す。
"""
import json
import sys
from pathlib import Path

GENERATOR_ROOT = Path.home() / "puzzle20261005"
SOURCE_GLOBS = [
    "verify/puzzles/*.json",
    "generated_puzzles/13x13/*/detail/puzzle.json",
]
OUTPUT_PATH = Path(__file__).parent / "puzzles_data.js"

FIELDS = ["rows", "cols", "clues"]


def puzzle_id_of(path):
    if path.name == "puzzle.json" and path.parent.name == "detail":
        return path.parent.parent.name  # 例: 001_13x13_min_obvious
    return path.stem  # 例: 001_sample_13x13


def load_puzzles():
    puzzles = []
    for pattern in SOURCE_GLOBS:
        for path in sorted(GENERATOR_ROOT.glob(pattern)):
            puzzle_id = puzzle_id_of(path)
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            if "id" in data and data["id"] != puzzle_id:
                sys.exit(f"id がパスと一致しません: {path} (id={data['id']})")
            entry = {"id": puzzle_id}
            for field in FIELDS:
                entry[field] = data[field]
            puzzles.append(entry)
    return puzzles


def main():
    puzzles = load_puzzles()
    if not puzzles:
        sys.exit(f"パズルが見つかりません: {GENERATOR_ROOT} / {SOURCE_GLOBS}")
    body = json.dumps(puzzles, ensure_ascii=False, indent=2)
    header = (
        "// コブリン問題データ。clues は [行, 列, 数字](0始まり)。\n"
        "// 001: 元盤面の各数字から上下左右に隣接する数字マスの数を引いて本来のコブリンへ変換したもの。\n"
    )
    OUTPUT_PATH.write_text(header + f"const PUZZLES = {body};\n", encoding="utf-8")
    print(f"{len(puzzles)} puzzles written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
