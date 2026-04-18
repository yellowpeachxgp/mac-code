#!/usr/bin/env bash
# build_wheel.sh — 构建 sdist + wheel
set -euo pipefail

cd "$(dirname "$0")/.."

python -m pip install --upgrade build twine

# 清理旧产物
rm -rf dist build *.egg-info

python -m build --sdist --wheel

echo ""
echo "产物："
ls -lh dist/

echo ""
echo "发布到 TestPyPI:"
echo "  python -m twine upload --repository testpypi dist/*"
echo ""
echo "发布到 PyPI（正式）:"
echo "  python -m twine upload dist/*"
