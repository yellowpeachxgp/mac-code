# 运行态提示

适用于：

- `图谱摘要`
- `列出不变式`
- `查看某条不变式`
- `自描述`
- `tenant 状态`
- `scene / memory / relation` 元信息

优先走 MCP：

- `we_together_self_describe`
- `we_together_list_invariants`
- `we_together_check_invariant`
- `we_together_graph_summary`

规则：

1. 先读 `references/local-runtime.md`
2. 使用其中声明的 MCP server 名称
3. 图谱类请求优先调 MCP，不先翻仓库源码
4. 如果用户要“列出不变式”，优先调 `we_together_list_invariants`
5. 如果用户要“查看某条不变式”，优先调 `we_together_check_invariant`
6. 如果 `graph_summary` 返回全 0：
   - 先说明这是当前 root 下默认 tenant 的空图谱/未初始化状态
   - 不把它误报成系统异常
