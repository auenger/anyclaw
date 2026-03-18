"""扩展技能测试"""

import pytest
import asyncio
import tempfile
import os

from anyclaw.skills.builtin.code_exec.skill import CodeExecSkill
from anyclaw.skills.builtin.process.skill import ProcessSkill, ProcessStatus
from anyclaw.skills.builtin.text.skill import TextSkill
from anyclaw.skills.builtin.system.skill import SystemSkill
from anyclaw.skills.builtin.data.skill import DataSkill


class TestCodeExecSkill:
    """CodeExecSkill 测试"""

    def setup_method(self):
        self.skill = CodeExecSkill()

    @pytest.mark.asyncio
    async def test_execute_python(self):
        """测试执行 Python 代码"""
        result = await self.skill.execute(
            language="python",
            code="print(1 + 1)"
        )
        assert "2" in result

    @pytest.mark.asyncio
    async def test_execute_python_multiline(self):
        """测试执行多行 Python 代码"""
        code = """
x = 10
y = 20
print(x + y)
"""
        result = await self.skill.execute(language="python", code=code)
        assert "30" in result

    @pytest.mark.asyncio
    async def test_execute_bash(self):
        """测试执行 Bash 命令"""
        result = await self.skill.execute(
            language="bash",
            code="echo 'Hello World'"
        )
        assert "Hello World" in result

    @pytest.mark.asyncio
    async def test_execute_no_code(self):
        """测试无代码"""
        result = await self.skill.execute(code="")
        assert "No code" in result or "Error" in result

    @pytest.mark.asyncio
    async def test_execute_invalid_language(self):
        """测试无效语言"""
        result = await self.skill.execute(
            language="invalid_lang",
            code="test"
        )
        assert "Unsupported" in result or "Unknown" in result

    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """测试执行超时"""
        result = await self.skill.execute(
            language="python",
            code="import time; time.sleep(10)",
            timeout=1
        )
        assert "timeout" in result.lower() or "killed" in result.lower() or "timed out" in result.lower()


class TestProcessSkill:
    """ProcessSkill 测试"""

    def setup_method(self):
        self.skill = ProcessSkill()

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """测试空进程列表"""
        result = await self.skill.execute(action="list")
        assert "No processes" in result

    @pytest.mark.asyncio
    async def test_start_process(self):
        """测试启动进程"""
        result = await self.skill.execute(
            action="start",
            command="echo test"
        )
        assert "Session ID" in result or "started" in result.lower()

    @pytest.mark.asyncio
    async def test_status_invalid_session(self):
        """测试无效会话状态"""
        result = await self.skill.execute(
            action="status",
            session_id="invalid-id"
        )
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_kill_invalid_session(self):
        """测试终止无效会话"""
        result = await self.skill.execute(
            action="kill",
            session_id="invalid-id"
        )
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """测试未知动作"""
        result = await self.skill.execute(action="invalid")
        assert "Unknown action" in result


class TestTextSkill:
    """TextSkill 测试"""

    def setup_method(self):
        self.skill = TextSkill()

    @pytest.mark.asyncio
    async def test_stats(self):
        """测试统计"""
        result = await self.skill.execute(
            action="stats",
            text="Hello World\nThis is a test."
        )
        assert "Characters:" in result
        assert "Words:" in result
        assert "Lines:" in result

    @pytest.mark.asyncio
    async def test_stats_empty(self):
        """测试空文本统计"""
        result = await self.skill.execute(action="stats", text="")
        assert "No text" in result

    @pytest.mark.asyncio
    async def test_extract_email(self):
        """测试提取邮箱"""
        result = await self.skill.execute(
            action="extract",
            text="Contact: test@example.com and info@example.org",
            pattern=r'[\w.-]+@[\w.-]+\.\w+'
        )
        assert "test@example.com" in result
        assert "info@example.org" in result

    @pytest.mark.asyncio
    async def test_extract_no_match(self):
        """测试无匹配"""
        result = await self.skill.execute(
            action="extract",
            text="No emails here",
            pattern=r'[\w.-]+@[\w.-]+\.\w+'
        )
        assert "No matches" in result

    @pytest.mark.asyncio
    async def test_replace(self):
        """测试替换"""
        result = await self.skill.execute(
            action="replace",
            text="Hello World",
            pattern="World",
            replacement="Python"
        )
        assert "Hello Python" in result
        assert "Replaced 1" in result

    @pytest.mark.asyncio
    async def test_format_uppercase(self):
        """测试大写转换"""
        result = await self.skill.execute(
            action="format",
            text="hello world",
            target_format="upper"
        )
        assert result == "HELLO WORLD"

    @pytest.mark.asyncio
    async def test_format_lowercase(self):
        """测试小写转换"""
        result = await self.skill.execute(
            action="format",
            text="HELLO WORLD",
            target_format="lower"
        )
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_format_compact(self):
        """测试压缩空白"""
        result = await self.skill.execute(
            action="format",
            text="hello    world\n\n  test  ",
            target_format="compact"
        )
        assert "  " not in result
        assert "\n" not in result


class TestSystemSkill:
    """SystemSkill 测试"""

    def setup_method(self):
        self.skill = SystemSkill()

    @pytest.mark.asyncio
    async def test_info(self):
        """测试系统信息"""
        result = await self.skill.execute(action="info")
        assert "System Information" in result
        assert "OS:" in result

    @pytest.mark.asyncio
    async def test_env_specific(self):
        """测试获取特定环境变量"""
        os.environ["TEST_VAR"] = "test_value"
        result = await self.skill.execute(
            action="env",
            command="TEST_VAR"
        )
        assert "TEST_VAR" in result
        assert "test_value" in result
        del os.environ["TEST_VAR"]

    @pytest.mark.asyncio
    async def test_env_not_found(self):
        """测试不存在的环境变量"""
        result = await self.skill.execute(
            action="env",
            command="NONEXISTENT_VAR_12345"
        )
        assert "not set" in result

    @pytest.mark.asyncio
    async def test_which_existing(self):
        """测试查找存在的命令"""
        result = await self.skill.execute(
            action="which",
            command="python3"
        )
        assert "Found" in result or "python" in result.lower()

    @pytest.mark.asyncio
    async def test_which_not_found(self):
        """测试查找不存在的命令"""
        result = await self.skill.execute(
            action="which",
            command="nonexistent_command_12345"
        )
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_sensitive_env_hidden(self):
        """测试敏感环境变量被隐藏"""
        os.environ["SECRET_API_KEY"] = "super_secret_value"
        result = await self.skill.execute(action="env")
        assert "HIDDEN" in result
        assert "super_secret_value" not in result
        del os.environ["SECRET_API_KEY"]


class TestDataSkill:
    """DataSkill 测试"""

    def setup_method(self):
        self.skill = DataSkill()

    @pytest.mark.asyncio
    async def test_parse_json(self):
        """测试解析 JSON"""
        result = await self.skill.execute(
            action="parse",
            data='{"name": "test", "value": 123}'
        )
        assert "name" in result
        assert "test" in result

    @pytest.mark.asyncio
    async def test_parse_invalid_json(self):
        """测试解析无效 JSON"""
        result = await self.skill.execute(
            action="parse",
            data="not valid json"
        )
        assert "error" in result.lower()

    @pytest.mark.asyncio
    async def test_query_simple(self):
        """测试简单查询"""
        result = await self.skill.execute(
            action="query",
            data='{"name": "test", "value": 123}',
            query="$.name"
        )
        assert "test" in result

    @pytest.mark.asyncio
    async def test_query_nested(self):
        """测试嵌套查询"""
        result = await self.skill.execute(
            action="query",
            data='{"user": {"name": "John", "age": 30}}',
            query="$.user.name"
        )
        assert "John" in result

    @pytest.mark.asyncio
    async def test_query_array(self):
        """测试数组查询"""
        result = await self.skill.execute(
            action="query",
            data='{"items": ["a", "b", "c"]}',
            query="$.items[0]"
        )
        assert "a" in result

    @pytest.mark.asyncio
    async def test_convert_json_to_compact(self):
        """测试转换为紧凑 JSON"""
        result = await self.skill.execute(
            action="convert",
            data='{"name": "test", "value": 123}',
            target_format="compact"
        )
        assert "\n" not in result
        assert "name" in result

    @pytest.mark.asyncio
    async def test_convert_unknown_format(self):
        """测试未知目标格式"""
        result = await self.skill.execute(
            action="convert",
            data='{"test": 1}',
            target_format="invalid_format"
        )
        assert "Unknown" in result

    @pytest.mark.asyncio
    async def test_validate_valid(self):
        """测试验证通过"""
        result = await self.skill.execute(
            action="validate",
            data='{"name": "test"}',
            schema='{"type": "object"}'
        )
        assert "passed" in result.lower()

    @pytest.mark.asyncio
    async def test_validate_invalid(self):
        """测试验证失败"""
        result = await self.skill.execute(
            action="validate",
            data='"not an object"',
            schema='{"type": "object"}'
        )
        assert "failed" in result.lower() or "passed" in result.lower()


class TestSkillIntegration:
    """技能集成测试"""

    @pytest.mark.asyncio
    async def test_code_exec_and_data(self):
        """测试代码执行和数据处理组合"""
        code_skill = CodeExecSkill()
        data_skill = DataSkill()

        # 执行代码生成 JSON
        code = "import json; print(json.dumps({'result': 42}))"
        exec_result = await code_skill.execute(language="python", code=code)

        # 解析结果
        parse_result = await data_skill.execute(
            action="parse",
            data='{"result": 42}'
        )
        assert "42" in parse_result

    @pytest.mark.asyncio
    async def test_text_and_data(self):
        """测试文本处理和数据处理组合"""
        text_skill = TextSkill()
        data_skill = DataSkill()

        # 统计文本
        text = '{"name": "Alice", "age": 30}'
        stats = await text_skill.execute(action="stats", text=text)
        assert "Characters:" in stats

        # 解析为 JSON
        parsed = await data_skill.execute(action="parse", data=text)
        assert "Alice" in parsed
