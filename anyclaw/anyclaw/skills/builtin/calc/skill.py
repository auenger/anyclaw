"""计算器技能

执行数学计算。
"""

import math
from anyclaw.skills.base import Skill


class CalcSkill(Skill):
    """Perform mathematical calculations"""

    async def execute(self, expression: str = "", **kwargs) -> str:
        """Evaluate mathematical expression

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Calculation result
        """
        if not expression:
            return "Please provide a mathematical expression"

        # 安全的数学函数
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }

        try:
            # 只允许数字、运算符和安全函数
            # 移除空格
            expr = expression.strip()

            # 验证表达式只包含允许的字符
            allowed_chars = set("0123456789+-*/.()%, ")
            for char in expr:
                if char.isalpha():
                    # 字母必须是安全函数名的一部分
                    pass
                elif char not in allowed_chars:
                    return f"Invalid character in expression: {char}"

            # 使用 eval 执行计算
            result = eval(expr, {"__builtins__": {}}, safe_dict)

            return f"Result: {result}"

        except ZeroDivisionError:
            return "Error: Division by zero"
        except SyntaxError:
            return "Error: Invalid expression syntax"
        except NameError as e:
            return f"Error: Unknown function or variable - {str(e)}"
        except Exception as e:
            return f"Error calculating: {str(e)}"
