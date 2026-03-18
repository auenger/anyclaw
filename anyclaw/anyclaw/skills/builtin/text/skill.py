"""文本处理技能

提供文本处理功能：统计、提取、替换、格式化。
"""

import re
import json
from typing import List, Optional

from anyclaw.skills.base import Skill


class TextSkill(Skill):
    """Text processing utilities"""

    async def execute(
        self,
        action: str = "stats",
        text: str = "",
        pattern: str = "",
        replacement: str = "",
        target_format: str = "",
        **kwargs
    ) -> str:
        """Execute text processing action

        Args:
            action: Operation to perform (stats, extract, replace, format)
            text: Input text to process
            pattern: Regex pattern (for extract/replace)
            replacement: Replacement string (for replace)
            target_format: Target format (for format action)

        Returns:
            Processing result
        """
        action = action.lower().strip()

        if action == "stats":
            return self._get_stats(text)
        elif action == "extract":
            return self._extract(text, pattern)
        elif action == "replace":
            return self._replace(text, pattern, replacement)
        elif action == "format":
            return self._format_text(text, target_format)
        else:
            return f"Unknown action: {action}. Available: stats, extract, replace, format"

    def _get_stats(self, text: str) -> str:
        """获取文本统计信息"""
        if not text:
            return "No text provided"

        lines = text.split('\n')
        words = text.split()
        chars = len(text)
        chars_no_space = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))

        # 句子统计（简单实现）
        sentences = len(re.findall(r'[.!?。！？]+', text))

        # 段落统计
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])

        stats = {
            "characters": chars,
            "characters_no_spaces": chars_no_space,
            "words": len(words),
            "lines": len(lines),
            "sentences": sentences,
            "paragraphs": paragraphs,
            "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        }

        lines = ["Text Statistics:", ""]
        lines.append(f"  Characters: {stats['characters']:,}")
        lines.append(f"  Characters (no spaces): {stats['characters_no_spaces']:,}")
        lines.append(f"  Words: {stats['words']:,}")
        lines.append(f"  Lines: {stats['lines']:,}")
        lines.append(f"  Sentences: {stats['sentences']}")
        lines.append(f"  Paragraphs: {stats['paragraphs']}")
        lines.append(f"  Avg word length: {stats['average_word_length']:.1f}")

        return "\n".join(lines)

    def _extract(self, text: str, pattern: str) -> str:
        """使用正则表达式提取匹配"""
        if not text:
            return "No text provided"
        if not pattern:
            return "No pattern provided"

        try:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)

            if not matches:
                return "No matches found"

            if len(matches) == 1:
                return f"Match: {matches[0]}"

            lines = [f"Found {len(matches)} matches:", ""]
            for i, match in enumerate(matches[:50], 1):  # 最多显示 50 个
                if isinstance(match, tuple):
                    lines.append(f"  {i}. {', '.join(match)}")
                else:
                    lines.append(f"  {i}. {match}")

            if len(matches) > 50:
                lines.append(f"  ... and {len(matches) - 50} more")

            return "\n".join(lines)

        except re.error as e:
            return f"Regex error: {str(e)}"

    def _replace(self, text: str, pattern: str, replacement: str) -> str:
        """搜索并替换"""
        if not text:
            return "No text provided"
        if not pattern:
            return "No pattern provided"

        try:
            # 统计匹配数
            matches = len(re.findall(pattern, text, re.MULTILINE))

            if matches == 0:
                return "No matches found to replace"

            # 执行替换
            result = re.sub(pattern, replacement, text, flags=re.MULTILINE)

            return f"Replaced {matches} occurrence(s)\n\n{result}"

        except re.error as e:
            return f"Regex error: {str(e)}"

    def _format_text(self, text: str, target_format: str) -> str:
        """格式转换"""
        if not text:
            return "No text provided"

        target_format = target_format.lower().strip()

        if target_format in ["json", "jsonl"]:
            return self._to_json(text)
        elif target_format in ["list", "lines"]:
            return self._to_lines(text)
        elif target_format in ["upper", "uppercase"]:
            return text.upper()
        elif target_format in ["lower", "lowercase"]:
            return text.lower()
        elif target_format in ["title", "titlecase"]:
            return text.title()
        elif target_format in ["strip", "trim"]:
            return text.strip()
        elif target_format in ["compact", "squeeze"]:
            # 压缩空白
            return re.sub(r'\s+', ' ', text).strip()
        else:
            return (f"Unknown format: {target_format}. "
                   f"Available: json, lines, upper, lower, title, strip, compact")

    def _to_json(self, text: str) -> str:
        """尝试转换为 JSON 格式"""
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]

        if len(lines) == 1:
            # 尝试解析为键值对
            if ':' in lines[0] or '=' in lines[0]:
                # 尝试解析
                pairs = re.split(r'[,;]\s*', lines[0])
                result = {}
                for pair in pairs:
                    if ':' in pair:
                        k, v = pair.split(':', 1)
                        result[k.strip()] = v.strip()
                    elif '=' in pair:
                        k, v = pair.split('=', 1)
                        result[k.strip()] = v.strip()
                return json.dumps(result, indent=2, ensure_ascii=False)

        # 返回行列表
        return json.dumps(lines, indent=2, ensure_ascii=False)

    def _to_lines(self, text: str) -> str:
        """转换为行列表"""
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        return "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))
