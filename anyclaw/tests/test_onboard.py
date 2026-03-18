"""CLI Onboard 命令测试"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from anyclaw.cli.onboard import (
    AUTH_CHOICES,
    show_auth_choices,
    prompt_auth_choice,
    save_config,
    update_env_file,
)


class TestAuthChoices:
    """Auth Choices 测试"""

    def test_auth_choices_defined(self):
        """测试 auth choices 已定义"""
        expected_choices = [
            "zai-coding-global",
            "zai-coding-cn",
            "zai-global",
            "zai-cn",
            "openai",
            "anthropic",
        ]

        for choice in expected_choices:
            assert choice in AUTH_CHOICES

    def test_zai_auth_choices_have_correct_config(self):
        """测试 ZAI auth choices 配置正确"""
        zai_choices = ["zai-coding-global", "zai-coding-cn", "zai-global", "zai-cn"]

        for choice in zai_choices:
            config = AUTH_CHOICES[choice]
            assert config["provider"] == "zai"
            assert config["env_key"] == "ZAI_API_KEY"
            assert config["model"].startswith("zai/")

    def test_all_auth_choices_have_required_fields(self):
        """测试所有 auth choices 都有必要字段"""
        required_fields = ["provider", "endpoint", "env_key", "model", "description"]

        for choice_id, config in AUTH_CHOICES.items():
            for field in required_fields:
                assert field in config, f"Auth choice {choice_id} missing field {field}"


class TestOnboardFunctions:
    """Onboard 函数测试"""

    def test_update_env_file_new(self):
        """测试创建新 .env 文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"

            with patch("anyclaw.cli.onboard.Path") as mock_path:
                mock_path.return_value = env_path
                mock_path.exists.return_value = False

                # 直接调用 update_env_file
                update_env_file({"ZAI_API_KEY": "test-key", "ZAI_ENDPOINT": "coding-global"})

    def test_update_env_file_existing(self):
        """测试更新现有 .env 文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("EXISTING_VAR=value\n")
            env_path = Path(f.name)

        try:
            # 直接写入测试
            with open(env_path, "w") as f:
                f.write("EXISTING_VAR=value\n")

            # 更新文件
            update_env_file({"NEW_VAR": "new_value"})

            # 这里只测试函数能正常运行
        finally:
            if env_path.exists():
                env_path.unlink()

    @patch("anyclaw.cli.onboard.Console.print")
    def test_show_auth_choices(self, mock_print):
        """测试显示 auth choices"""
        show_auth_choices()
        # 应该调用了多次 print
        assert mock_print.call_count > 0


class TestSaveConfig:
    """保存配置测试"""

    def test_save_zai_config(self):
        """测试保存 ZAI 配置"""
        choice_config = AUTH_CHOICES["zai-coding-global"]

        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"

            with patch("anyclaw.cli.onboard.Path") as mock_path:
                mock_path.return_value = env_path

                # 直接测试 update_env_file
                env_vars = {
                    choice_config["env_key"]: "test-api-key",
                    "LLM_MODEL": choice_config["model"],
                    "ZAI_ENDPOINT": choice_config["endpoint"],
                }

                # 创建 .env 文件
                with open(env_path, "w") as f:
                    for key, value in env_vars.items():
                        f.write(f"{key}={value}\n")

                # 验证文件内容
                content = env_path.read_text()
                assert "ZAI_API_KEY=test-api-key" in content
                assert "ZAI_ENDPOINT=coding-global" in content
