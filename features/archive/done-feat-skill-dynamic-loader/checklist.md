# Checklist: Skill 动态加载修复

## 开发前

- [ ] 确认 feat-skill-toolkit 已完成
- [ ] 备份现有 loader.py
- [ ] 理解 importlib.util API
- [ ] 创建 feature 分支

## Phase 1: 修复动态加载

### loader.py 重构
- [ ] 移除 `anyclaw.skills.builtin.{name}.skill` 硬编码
- [ ] 使用 `spec_from_file_location()` 动态加载
- [ ] 生成唯一模块名避免冲突
- [ ] 添加 `sys.modules` 管理
- [ ] 添加类型提示

### 多目录扫描
- [ ] 实现 `_scan_directory(dir, priority)` 方法
- [ ] 按优先级合并：workspace > managed > bundled
- [ ] 记录 skill 来源 (`source: "workspace"|"managed"|"bundled"`)
- [ ] 处理目录不存在的情况

## Phase 2: .skill 文件安装

### installer.py (新文件)
- [ ] 创建 `install_skill(source, target_dir)` 函数
- [ ] ZIP 解压逻辑 (`.skill` 文件)
- [ ] 目录复制逻辑 (文件夹)
- [ ] 安装后调用 `validate_skill()`
- [ ] 失败时清理临时文件
- [ ] 返回安装路径

### CLI 命令
- [ ] `anyclaw skill install <path>` 命令
- [ ] 支持 `.skill` 和目录两种来源
- [ ] `--force` 覆盖标志
- [ ] 安装进度显示
- [ ] 成功/失败消息

## Phase 3: 热重载

### loader.py 热重载
- [ ] 实现 `reload_skill(name: str)` 方法
- [ ] 实现 `reload_all()` 方法
- [ ] 清理 `sys.modules` 缓存
- [ ] 清理 `self.python_skills` 缓存
- [ ] 重新加载并返回新实例

### CLI 命令
- [ ] `anyclaw skill reload` 命令
- [ ] `anyclaw skill reload <name>` 指定单个
- [ ] 显示重载统计

## Phase 4: 配置支持

### settings.py
- [ ] 添加 `skills_dirs: List[str]` 配置
- [ ] 默认值：`["bundled", "managed", "workspace"]`
- [ ] 支持环境变量覆盖

## Phase 5: 测试

- [ ] 任意路径 Python skill 加载测试
- [ ] 多目录优先级合并测试
- [ ] .skill 文件安装测试
- [ ] 目录安装测试
- [ ] 热重载测试
- [ ] 边界条件测试

## 验收测试

- [ ] 在 workspace/skills/ 创建 Python skill，验证加载
- [ ] 在 managed-skills/ 创建同名 skill，验证覆盖
- [ ] 安装 .skill 文件，验证解压和验证
- [ ] 修改 skill.py，执行 reload，验证新代码生效
- [ ] 运行 `anyclaw skill list`，验证来源显示

## 完成后

- [ ] 运行完整测试套件
- [ ] 更新 CLAUDE.md 文档
- [ ] 更新 project_context.md
- [ ] 提交代码
