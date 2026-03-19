# Task: Skill 动态加载修复

## 任务分解

### Phase 1: 修复动态加载

#### Task 1.1: 重构 load_python_skill
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [ ] 移除硬编码的 `anyclaw.skills.builtin.*` 路径
- [ ] 使用 `importlib.util.spec_from_file_location`
- [ ] 动态生成唯一模块名
- [ ] 正确处理模块缓存

#### Task 1.2: 多目录扫描
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [ ] 按优先级顺序扫描目录
- [ ] workspace > managed > bundled
- [ ] 同名 skill 覆盖逻辑
- [ ] 记录 skill 来源目录

### Phase 2: .skill 文件安装

#### Task 2.1: 安装功能
**文件**: `anyclaw/skills/toolkit/installer.py` (新文件)
**内容**:
- [ ] `install_skill(source, target_dir)` 函数
- [ ] ZIP 解压逻辑
- [ ] 目录复制逻辑
- [ ] 安装后验证
- [ ] 覆盖确认逻辑

#### Task 2.2: CLI 命令
**文件**: `anyclaw/cli/skill_cmd.py`
**内容**:
- [ ] `anyclaw skill install <path>` 命令
- [ ] 支持 .skill 文件和目录
- [ ] 安装进度显示
- [ ] 错误处理

### Phase 3: 热重载

#### Task 3.1: 热重载实现
**文件**: `anyclaw/skills/loader.py`
**内容**:
- [ ] `reload_skill(name)` 方法
- [ ] `reload_all()` 方法
- [ ] 模块缓存清理
- [ ] 实例重建

#### Task 3.2: CLI 命令
**文件**: `anyclaw/cli/skill_cmd.py`
**内容**:
- [ ] `anyclaw skill reload [name]` 命令
- [ ] 重载进度显示
- [ ] 结果统计

### Phase 4: 配置支持

#### Task 4.1: Skills 目录配置
**文件**: `anyclaw/config/settings.py`
**内容**:
- [ ] 添加 `skills_dirs` 配置项
- [ ] 默认目录：bundled/managed/workspace
- [ ] 支持自定义目录

### Phase 5: 测试

#### Task 5.1: 单元测试
**文件**: `tests/test_skill_loader.py`
**内容**:
- [ ] 任意路径加载测试
- [ ] 优先级合并测试
- [ ] 安装功能测试
- [ ] 热重载测试

## 执行顺序

1. Task 1.1 - 修复核心加载问题
2. Task 1.2 - 多目录支持
3. Task 4.1 - 配置支持
4. Task 2.1 + 2.2 - 安装功能
5. Task 3.1 + 3.2 - 热重载
6. Task 5.1 - 测试

## 依赖关系

```
loader.py 修复 ──> 多目录扫描 ──> 配置支持
       │
       └──> installer.py ──> CLI
       │
       └──> 热重载 ──> CLI
```

## 预计工作量

| 阶段 | 预计时间 |
|------|----------|
| Phase 1 | 2h |
| Phase 2 | 1.5h |
| Phase 3 | 1h |
| Phase 4 | 0.5h |
| Phase 5 | 1h |
| **总计** | **6h** |
