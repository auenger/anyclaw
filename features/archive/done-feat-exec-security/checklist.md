# 完成检查清单

## 代码实现

- [ ] `anyclaw/tools/guards.py` 已创建
- [ ] `CORE_DENY_PATTERNS` 包含所有危险命令类型：
  - [ ] rm -rf (Unix)
  - [ ] del /f /q, rmdir /s (Windows)
  - [ ] dd if=
  - [ ] mkfs, diskpart, format
  - [ ] shutdown, reboot, poweroff, halt
  - [ ] fork bomb
  - [ ] 写入 /dev/sd*
- [ ] `anyclaw/tools/shell.py` 已改造
- [ ] 核心保护逻辑优先于用户配置
- [ ] `anyclaw/config/settings.py` 已添加 SecuritySettings
- [ ] 支持 deny_patterns 配置
- [ ] 支持 allow_patterns 配置
- [ ] `anyclaw/cli/app.py` 已添加 security 命令

## 测试

- [ ] `tests/test_exec_guard.py` 已创建
- [ ] 核心保护测试覆盖所有模式
- [ ] 用户 deny_patterns 测试通过
- [ ] allow_patterns 白名单测试通过
- [ ] 配置优先级测试通过
- [ ] 测试覆盖率 > 80%

## 文档

- [ ] `anyclaw/templates/TOOLS.md` 已更新安全限制说明
- [ ] CLI 命令有帮助文档
- [ ] 代码有适当注释

## 验收

- [ ] 核心保护不可通过配置绕过
- [ ] 用户可添加自定义安全规则
- [ ] 用户可启用白名单模式
- [ ] `anyclaw security show` 正确显示规则
- [ ] 所有测试通过：`poetry run pytest tests/test_exec_guard.py -v`

## 兼容性

- [ ] 不破坏现有 ExecTool API
- [ ] 配置文件向后兼容
- [ ] 默认行为与当前一致（除新增的保护）
