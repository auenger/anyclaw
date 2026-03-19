"""ExecTool 安全保护测试"""

import pytest
import asyncio

from anyclaw.tools.guards import CoreGuard, UserGuard, CommandGuard
from anyclaw.tools.shell import ExecTool


class TestCoreGuard:
    """核心保护层测试"""

    def test_rm_rf_blocked(self):
        """测试 rm -rf 被阻止"""
        blocked, reason = CoreGuard.check("rm -rf /")
        assert blocked is True
        assert "递归强制删除" in reason

    def test_rm_variations(self):
        """测试 rm 各种变体"""
        dangerous_commands = [
            "rm -rf /home",
            "rm -fr /tmp",
            "rm -r -f /var",
            "sudo rm -rf /",
        ]
        for cmd in dangerous_commands:
            blocked, _ = CoreGuard.check(cmd)
            assert blocked is True, f"应该阻止: {cmd}"

    def test_dd_blocked(self):
        """测试 dd 命令被阻止"""
        blocked, reason = CoreGuard.check("dd if=/dev/zero of=/dev/sda")
        assert blocked is True
        assert "磁盘" in reason

    def test_shutdown_blocked(self):
        """测试关机命令被阻止"""
        for cmd in ["shutdown -h now", "reboot", "poweroff", "halt"]:
            blocked, reason = CoreGuard.check(cmd)
            assert blocked is True, f"应该阻止: {cmd}"
            assert "关机" in reason or "重启" in reason

    def test_disk_write_blocked(self):
        """测试直接写入磁盘被阻止"""
        blocked, reason = CoreGuard.check("echo data > /dev/sda")
        assert blocked is True
        assert "磁盘" in reason

    def test_mkfs_blocked(self):
        """测试格式化命令被阻止"""
        blocked, reason = CoreGuard.check("mkfs.ext4 /dev/sda1")
        assert blocked is True
        assert "格式化" in reason

    def test_chmod_777_blocked(self):
        """测试危险权限设置被阻止"""
        blocked, reason = CoreGuard.check("chmod 777 /etc/passwd")
        assert blocked is True
        assert "777" in reason

    def test_safe_commands_allowed(self):
        """测试安全命令不被阻止"""
        safe_commands = [
            "ls -la",
            "cat /etc/hosts",
            "echo hello",
            "git status",
            "npm install",
            "python script.py",
            "curl https://example.com",
        ]
        for cmd in safe_commands:
            blocked, reason = CoreGuard.check(cmd)
            assert blocked is False, f"不应该阻止: {cmd}"

    def test_windows_commands_blocked(self):
        """测试 Windows 危险命令被阻止"""
        windows_commands = [
            "del /f /q file.txt",
            "rmdir /s /q folder",
            "rd /s /q folder",
        ]
        for cmd in windows_commands:
            blocked, reason = CoreGuard.check(cmd)
            assert blocked is True, f"应该阻止 Windows 命令: {cmd}"


class TestUserGuard:
    """用户自定义保护层测试"""

    def test_user_deny_patterns(self):
        """测试用户 deny 模式"""
        guard = UserGuard(deny_patterns=[r"npm publish", r"git push --force"])

        blocked, reason = guard.check("npm publish")
        assert blocked is True
        assert "用户安全策略" in reason

        blocked, reason = guard.check("git push --force origin main")
        assert blocked is True

        # 安全命令不应该被阻止
        blocked, _ = guard.check("npm install")
        assert blocked is False

    def test_user_allow_patterns(self):
        """测试用户白名单模式"""
        guard = UserGuard(allow_patterns=[r"^git status$", r"^ls"])

        # 在白名单中的命令允许
        blocked, _ = guard.check("git status")
        assert blocked is False

        blocked, _ = guard.check("ls -la")
        assert blocked is False

        # 不在白名单中的命令被阻止
        blocked, reason = guard.check("npm install")
        assert blocked is True
        assert "不在允许列表" in reason

    def test_empty_config(self):
        """测试空配置（默认允许所有）"""
        guard = UserGuard()

        blocked, _ = guard.check("rm -rf /")  # 用户层不阻止，由核心层阻止
        assert blocked is False


class TestCommandGuard:
    """命令保护器测试（核心 + 用户组合）"""

    def test_core_guard_priority(self):
        """测试核心保护优先级最高"""
        # 即使清空用户配置，核心保护仍然生效
        guard = CommandGuard(
            user_deny_patterns=[],
            user_allow_patterns=[r".*"],  # 尝试用白名单绕过
        )

        # 核心保护命令仍然被阻止
        blocked, reason = guard.check("rm -rf /")
        assert blocked is True
        assert "CoreGuard" in reason

    def test_user_deny_after_core(self):
        """测试用户 deny 在核心保护后生效"""
        guard = CommandGuard(
            user_deny_patterns=[r"npm publish"],
        )

        # 用户自定义阻止
        blocked, reason = guard.check("npm publish")
        assert blocked is True
        assert "UserGuard" in reason

        # 安全命令允许
        blocked, _ = guard.check("npm install")
        assert blocked is False

    def test_combined_protection(self):
        """测试组合保护"""
        guard = CommandGuard(
            user_deny_patterns=[r"npm publish"],
            user_allow_patterns=[],
        )

        # 核心保护
        blocked, reason = guard.check("rm -rf /")
        assert blocked is True
        assert "CoreGuard" in reason

        # 用户保护
        blocked, reason = guard.check("npm publish")
        assert blocked is True
        assert "UserGuard" in reason

        # 安全命令
        blocked, _ = guard.check("npm install")
        assert blocked is False

    def test_get_all_rules(self):
        """测试获取所有规则"""
        guard = CommandGuard(
            user_deny_patterns=[r"npm publish"],
            user_allow_patterns=[r"^ls"],
        )

        rules = guard.get_all_rules()

        assert "core" in rules
        assert "user" in rules
        assert len(rules["core"]["patterns"]) > 0
        assert len(rules["user"]["deny_patterns"]) == 1
        assert len(rules["user"]["allow_patterns"]) == 1
        assert rules["user"]["allow_mode"] is True


class TestExecToolIntegration:
    """ExecTool 集成测试"""

    @pytest.mark.asyncio
    async def test_dangerous_command_blocked(self):
        """测试危险命令被阻止"""
        tool = ExecTool()

        result = await tool.execute("rm -rf /")
        assert "被安全策略阻止" in result
        assert "CoreGuard" in result

    @pytest.mark.asyncio
    async def test_user_deny_blocked(self):
        """测试用户自定义阻止"""
        tool = ExecTool(deny_patterns=[r"npm publish"])

        result = await tool.execute("npm publish")
        assert "被安全策略阻止" in result
        assert "UserGuard" in result

    @pytest.mark.asyncio
    async def test_safe_command_executed(self):
        """测试安全命令可以执行"""
        tool = ExecTool()

        # 使用一个简单的命令测试
        result = await tool.execute("echo 'hello world'")
        assert "hello world" in result
        assert "被安全策略阻止" not in result

    @pytest.mark.asyncio
    async def test_core_cannot_be_bypassed(self):
        """测试核心保护不可绕过"""
        # 尝试用 allow_patterns 绕过
        tool = ExecTool(allow_patterns=[r".*"])

        result = await tool.execute("rm -rf /")
        assert "被安全策略阻止" in result
        assert "CoreGuard" in result

    def test_guard_property_accessible(self):
        """测试 guard 属性可访问"""
        tool = ExecTool()
        assert hasattr(tool, "guard")
        assert isinstance(tool.guard, CommandGuard)


class TestEdgeCases:
    """边界情况测试"""

    def test_case_insensitive(self):
        """测试大小写不敏感"""
        blocked, _ = CoreGuard.check("RM -RF /")
        assert blocked is True

        blocked, _ = CoreGuard.check("SHUTDOWN -H NOW")
        assert blocked is True

    def test_command_with_pipes(self):
        """测试带管道的命令"""
        blocked, _ = CoreGuard.check("cat file | rm -rf /")
        assert blocked is True

    def test_command_with_subshell(self):
        """测试带子 shell 的命令"""
        blocked, _ = CoreGuard.check("$(rm -rf /)")
        assert blocked is True

    def test_whitespace_variations(self):
        """测试空白字符变体"""
        blocked, _ = CoreGuard.check("rm   -rf   /")
        assert blocked is True

        blocked, _ = CoreGuard.check("  rm -rf /  ")
        assert blocked is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
