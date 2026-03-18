# Feature Workflow 测试目录

本目录包含 Feature Workflow 的测试报告和 Review 文档。

## 测试报告列表

| 日期 | 文件 | 描述 | 状态 |
|------|------|------|------|
| 2026-03-02 | [mvp-flow-test.md](./2026-03-02-mvp-flow-test.md) | MVP 完整流程测试 | ✅ 通过 |

## 测试覆盖范围

### Phase 1: 核心 Skills
- [x] new-feature
- [x] start-feature
- [x] implement-feature
- [x] verify-feature
- [x] complete-feature
- [x] list-features

### Phase 2: 管理 Skills
- [x] block-feature
- [x] unblock-feature
- [x] feature-config
- [ ] cleanup-features (待测试)

### Phase 3: Workflows
- [ ] feature-lifecycle (待测试)
- [ ] auto-schedule (待测试)

### Phase 4: Agents
- [ ] feature-manager (待测试)
- [ ] dev-agent (待测试)

## 如何添加新测试

1. 创建新的测试文件: `YYYY-MM-DD-test-name.md`
2. 按照模板格式填写测试内容
3. 更新本文件中的测试报告列表

## 测试文件模板

```markdown
# 测试名称

**测试日期**: YYYY-MM-DD
**测试人员**: 姓名
**测试环境**: 系统信息
**测试范围**: 测试的功能范围

## 1. 测试概述
...

## 2. 测试执行记录
...

## 3. 测试结果
...

## 4. 结论
...
```
