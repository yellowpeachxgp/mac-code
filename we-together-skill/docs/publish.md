# Publishing `we-together-skill` to PyPI

## 前置

- 注册 [PyPI](https://pypi.org) 账号 + 2FA
- 注册 [TestPyPI](https://test.pypi.org) 账号（用于预发）
- 在 `~/.pypirc` 配置 API token（或导出 `TWINE_USERNAME=__token__` + `TWINE_PASSWORD=pypi-...`）
- GitHub 仓库添加 secret `PYPI_TOKEN` 开启 tag-push 自动发布（见 `.github/workflows/publish.yml`）

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

### 3. 本地验证

```bash
pip install --force-reinstall dist/we_together_skill-*.whl
we-together version
```

### 4. 发布 TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
# 从 TestPyPI 安装验证：
pip install -i https://test.pypi.org/simple/ we-together-skill
```

### 5. 发布 PyPI（正式）

```bash
python -m twine upload dist/*
```

### 6. Tag + 推送（自动发布）

```bash
git tag vX.Y.Z
git push --tags
# GitHub Actions publish.yml 会自动 build + upload（需 PYPI_TOKEN secret）
```

## Checklist

- [ ] pyproject.version 与 cli.VERSION 一致
- [ ] CHANGELOG 有该版本条目
- [ ] 所有 ADR 已 Accepted
- [ ] pytest 全绿
- [ ] eval-relation 不回归
- [ ] README 顶部链接到最新 CHANGELOG
- [ ] docs/quickstart.md 命令全部可跑通
- [ ] schema 版本与 docs 同步

## Release Notes 模板

见 `docs/release_notes_template.md`
