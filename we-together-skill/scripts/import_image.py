"""scripts/import_image.py — 把一张图走 OCR → 写 media_asset + memory。

用法:
  python scripts/import_image.py --root . --image path/to.jpg \\
      --owner person_alice --scene scene_x --visibility shared
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from we_together.llm.providers.vision import MockVisionLLMClient
from we_together.services.ocr_service import ocr_to_memory


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--image", required=True)
    ap.add_argument("--owner", required=True)
    ap.add_argument("--scene", default=None)
    ap.add_argument("--visibility", default="shared",
                    choices=["private", "shared", "group"])
    args = ap.parse_args()

    root = Path(args.root).resolve()
    db = root / "db" / "main.sqlite3"
    img = Path(args.image).resolve()
    if not img.exists():
        print(json.dumps({"error": "image not found"}))
        return 1
    if not db.exists():
        print(json.dumps({"error": "db not found"}))
        return 1

    # 默认 Mock Vision；如需真 client 在此切换
    vision = MockVisionLLMClient(
        default_description=f"[imported image: {img.name}]",
    )
    result = ocr_to_memory(
        db, image_bytes=img.read_bytes(),
        owner_id=args.owner, scene_id=args.scene,
        visibility=args.visibility, vision_client=vision,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
