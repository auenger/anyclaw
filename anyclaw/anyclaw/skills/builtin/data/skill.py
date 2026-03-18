"""数据处理技能

处理 JSON 和 YAML 数据。
"""

import json
import re
from typing import Any, Optional

from anyclaw.skills.base import Skill


class DataSkill(Skill):
    """JSON/YAML data processing"""

    async def execute(
        self,
        action: str = "parse",
        data: str = "",
        format: str = "json",
        query: str = "",
        target_format: str = "",
        schema: str = "",
        **kwargs
    ) -> str:
        """Execute data processing action

        Args:
            action: Operation to perform (parse, query, convert, validate)
            data: Input data string
            format: Input format (json, yaml)
            query: JSONPath query (for query action)
            target_format: Target format (for convert action)
            schema: JSON Schema string (for validate action)

        Returns:
            Processing result
        """
        action = action.lower().strip()

        if action == "parse":
            return self._parse(data, format)
        elif action == "query":
            return self._query(data, query)
        elif action == "convert":
            return self._convert(data, format, target_format)
        elif action == "validate":
            return self._validate(data, schema)
        else:
            return f"Unknown action: {action}. Available: parse, query, convert, validate"

    def _parse(self, data: str, format: str) -> str:
        """解析数据"""
        if not data:
            return "No data provided"

        format = format.lower()

        try:
            if format in ["json", "jsonl"]:
                parsed = json.loads(data)
            elif format in ["yaml", "yml"]:
                try:
                    import yaml
                    parsed = yaml.safe_load(data)
                except ImportError:
                    return "YAML support requires PyYAML: pip install pyyaml"
            else:
                return f"Unknown format: {format}. Available: json, yaml"

            # 格式化输出
            return self._format_output(parsed)

        except json.JSONDecodeError as e:
            return f"JSON parse error: {str(e)}"
        except Exception as e:
            return f"Parse error: {str(e)}"

    def _query(self, data: str, query: str) -> str:
        """JSONPath 查询"""
        if not data:
            return "No data provided"
        if not query:
            return "No query provided"

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError as e:
            return f"JSON parse error: {str(e)}"

        # 简单的 JSONPath 实现
        # 支持基本的路径表达式：$.store.book[0].title
        try:
            results = self._jsonpath_query(parsed, query)

            if not results:
                return "No matches found"

            if len(results) == 1:
                return self._format_output(results[0])

            return self._format_output(results)

        except Exception as e:
            return f"Query error: {str(e)}"

    def _convert(self, data: str, from_format: str, to_format: str) -> str:
        """格式转换"""
        if not data:
            return "No data provided"

        from_format = from_format.lower()
        to_format = to_format.lower()

        # 解析输入
        try:
            if from_format in ["json", "jsonl"]:
                parsed = json.loads(data)
            elif from_format in ["yaml", "yml"]:
                try:
                    import yaml
                    parsed = yaml.safe_load(data)
                except ImportError:
                    return "YAML support requires PyYAML: pip install pyyaml"
            else:
                return f"Unknown source format: {from_format}"
        except Exception as e:
            return f"Parse error: {str(e)}"

        # 转换输出
        try:
            if to_format in ["json"]:
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            elif to_format in ["yaml", "yml"]:
                try:
                    import yaml
                    return yaml.dump(parsed, allow_unicode=True, default_flow_style=False)
                except ImportError:
                    return "YAML support requires PyYAML: pip install pyyaml"
            elif to_format in ["compact", "minify"]:
                return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
            elif to_format in ["python", "repr"]:
                return repr(parsed)
            else:
                return f"Unknown target format: {to_format}. Available: json, yaml, compact, python"
        except Exception as e:
            return f"Convert error: {str(e)}"

    def _validate(self, data: str, schema: str) -> str:
        """JSON Schema 验证"""
        if not data:
            return "No data provided"
        if not schema:
            return "No schema provided"

        try:
            parsed_data = json.loads(data)
            parsed_schema = json.loads(schema)
        except json.JSONDecodeError as e:
            return f"JSON parse error: {str(e)}"

        try:
            import jsonschema
            jsonschema.validate(parsed_data, parsed_schema)
            return "✅ Validation passed"
        except jsonschema.ValidationError as e:
            return f"❌ Validation failed:\n  Path: {' -> '.join(str(p) for p in e.path)}\n  Error: {e.message}"
        except ImportError:
            # 简单的类型检查（无 jsonschema 库时）
            return self._simple_validate(parsed_data, parsed_schema)

    def _simple_validate(self, data: Any, schema: dict) -> str:
        """简单验证（无 jsonschema 库时使用）"""
        schema_type = schema.get("type")

        if schema_type:
            type_map = {
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "array": list,
                "object": dict,
            }
            expected_type = type_map.get(schema_type)
            if expected_type and not isinstance(data, expected_type):
                return f"❌ Type mismatch: expected {schema_type}, got {type(data).__name__}"

        return "✅ Basic validation passed (install jsonschema for full validation)"

    def _jsonpath_query(self, data: Any, query: str) -> list:
        """简单的 JSONPath 查询实现"""
        # 移除开头的 $.
        if query.startswith("$."):
            query = query[2:]
        elif query.startswith("$"):
            query = query[1:]

        if not query:
            return [data]

        results = [data]
        parts = self._split_path(query)

        for part in parts:
            new_results = []
            for current in results:
                if isinstance(current, dict):
                    if part in current:
                        new_results.append(current[part])
                    elif part == "*":
                        new_results.extend(current.values())
                elif isinstance(current, list):
                    try:
                        idx = int(part)
                        if 0 <= idx < len(current):
                            new_results.append(current[idx])
                    except ValueError:
                        if part == "*":
                            new_results.extend(current)
            results = new_results

        return results

    def _split_path(self, path: str) -> list:
        """分割路径表达式"""
        # 处理 . 分隔和 [index] 语法
        parts = []
        current = ""

        i = 0
        while i < len(path):
            char = path[i]

            if char == ".":
                if current:
                    parts.append(current)
                    current = ""
            elif char == "[":
                if current:
                    parts.append(current)
                    current = ""
                # 找到匹配的 ]
                j = i + 1
                while j < len(path) and path[j] != "]":
                    j += 1
                parts.append(path[i+1:j])
                i = j
            else:
                current += char

            i += 1

        if current:
            parts.append(current)

        return parts

    def _format_output(self, data: Any) -> str:
        """格式化输出"""
        if isinstance(data, str):
            return data
        return json.dumps(data, indent=2, ensure_ascii=False)
