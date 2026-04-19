# PyPI Release Checklist

v0.17.0 发布到 PyPI 前的检查清单（Phase 56 / ADR 0058）。

## 0. 前置条件

- [ ] `v{NEW_VERSION}` git tag 已创建
- [ ] 全量 pytest 绿（期望当前基线全部通过）
- [ ] wheel 本地隔离 venv 安装验证通过
- [ ] CHANGELOG 含本版本条目
- [ ] 至少一个 Core Maintainer 批准
- [ ] `pip install -e .[vector]` 成功（native backend extras）
- [ ] `bench_scale.py --backend sqlite_vec/faiss` smoke 通过
- [ ] federation HTTP smoke 通过（含 bearer + POST `/federation/v1/memories` 若本版本启用写路径）

## 1. 准备包

```bash
rm -rf dist/ build/ *.egg-info
.venv/bin/python -m build --wheel --sdist
```

期望产出：
- `dist/we_together-{NEW_VERSION}-py3-none-any.whl`
- `dist/we_together-{NEW_VERSION}.tar.gz`

可选 native backend smoke：

```bash
.venv/bin/pip install -e .[vector]
.venv/bin/python scripts/bootstrap.py --root /tmp/wt_release_check
.venv/bin/python scripts/bench_scale.py --root /tmp/wt_release_check --n 100 --queries 3 --backend sqlite_vec
.venv/bin/python scripts/bench_scale.py --root /tmp/wt_release_check --n 100 --queries 3 --backend faiss
```

HTTP smoke：

```bash
bash scripts/federation_e2e_smoke.sh
```

## 2. 元数据自检

```bash
.venv/bin/python -m twine check dist/*
```

所有 `PASSED`。

## 3. TestPyPI dry-run

```bash
# 首次需在 https://test.pypi.org/ 注册 API token
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-testpypi-token>

.venv/bin/python -m twine upload --repository testpypi dist/*
```

从 TestPyPI 隔离 venv 安装验证：

```bash
python3 -m venv /tmp/we_tg_test && source /tmp/we_tg_test/bin/activate
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    we-together=={NEW_VERSION}
we-together version
```

## 4. PyPI 正式发布

```bash
export TWINE_PASSWORD=pypi-<your-pypi-token>
.venv/bin/python -m twine upload dist/*
```

发布后等待 ~2 分钟，然后：

```bash
pip install we-together=={NEW_VERSION}
we-together version
```

## 5. 发布后

- [ ] GitHub Release 创建（附 `dist/*.whl` + release_notes）
- [ ] Homepage / Docs 更新版本号
- [ ] Tweet / Discord 公告
- [ ] 关闭对应 milestone

## 故障排查

- **401 Unauthorized**：token 过期或错误；去 https://pypi.org/manage/account/token/ 重新生成
- **400 File already exists**：版本号不能覆盖，必须 bump
- **Wheel 包名冲突**：`pyproject.toml` 的 `name` 需在 PyPI 未被占用

## 相关文档

- [GOVERNANCE.md](../../GOVERNANCE.md)
- [SECURITY.md](../../SECURITY.md)
- [CHANGELOG.md](../CHANGELOG.md)
