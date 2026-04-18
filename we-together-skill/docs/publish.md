# Publishing `we-together-skill` to PyPI

## 前置

- 注册 [PyPI](https://pypi.org) 账号 + 2FA
- 注册 [TestPyPI](https://test.pypi.org) 账号（用于预发）
- 在 `~/.pypirc` 配置 API token（或导出 `TWINE_USERNAME=__token__` + `TWINE_PASSWORD=pypi-...`）

## 流程

### 1. 更新版本

```bash
# 编辑 pyproject.toml 的 [project].version
# 同步 src/we_together/cli.py 的 VERSION
```

### 2. 构建

```bash
bash scripts/build_wheel.sh
```

产物：`dist/we_together_skill-<v>.tar.gz` + `dist/we_together_skill-<v>-py3-none-any.whl`

### 3. 本地验证

```bash
pip install --force-reinstall dist/we_together_skill-*.whl
we-together version   # 应输出当前版本
```

### 4. 发布 TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
# 然后从 TestPyPI 安装验证：
pip install -i https://test.pypi.org/simple/ we-together-skill
```

### 5. 发布 PyPI（正式）

```bash
python -m twine upload dist/*
```

### 6. Tag + 推送

```bash
git tag v0.X.Y
git push --tags
```

## Checklist

- [ ] pyproject.version 与 cli.VERSION 一致
- [ ] CHANGELOG 有该版本条目
- [ ] 所有 ADR 已 Accepted
- [ ] pytest 全绿（`.venv/bin/python -m pytest -q`）
- [ ] eval-relation 不回归（`eval/baseline.json` 仍通过）
- [ ] README 顶部链接到最新 CHANGELOG
- [ ] docs/quickstart.md 命令全部可跑通
