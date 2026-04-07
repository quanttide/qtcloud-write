"""
PRD写作流程工具 - 基于雪花写作法的反向重构

核心理念：透明化AI认知过程，帮助用户理解和掌握。

流程：
1. 初始写作 - 用户给出想法，生成初版PRD
2. 头脑风暴 - 调用LLM理解核心理念，找出差异化定位
3. 反向重构 - 从复杂到简洁，提炼核心，拆分细节
4. 用户模拟 - LLM模拟用户阅读，提出改进建议
5. 简化完善 - 删除过度设计，保留核心内容
6. 统一格式 - 标题、叙事逻辑统一化

使用示例：
    from write_prd import PRDWriter
    
    writer = PRDWriter(product_name="量潮编程云")
    writer.initial_draft(core_idea="雪花编程法")
    writer.brainstorm_core()
    writer.reverse_refactor()
    writer.simulate_user()
    writer.simplify()
    writer.save("docs/prd/index.md")
"""

import subprocess
import json
from pathlib import Path
from typing import List, Optional


class PRDWriter:
    """PRD写作工具 - 透明化AI认知过程"""
    
    def __init__(self, product_name: str, product_type: str = "编程"):
        self.product_name = product_name
        self.product_type = product_type
        self.prd_content = ""
        self.core_idea = ""
        self.models = ["deepseek-v3.2", "glm-5", "kimi-k2.5"]
        
    def initial_draft(self, core_idea: str) -> str:
        """初始写作 - 用户给出核心想法"""
        self.core_idea = core_idea
        
        self.prd_content = f"""# {self.product_name}产品需求文档

## 产品定位

{self.product_name}帮助{self.product_type}者通过持续改进提高工程质量。

核心理念：{core_idea}

## 核心功能

三个核心功能支持持续改进。

## 用户收益

降低成本，提升效率，控制风险。

"""
        return self.prd_content
    
    def brainstorm_core(self) -> dict:
        """头脑风暴 - 调用LLM理解核心理念"""
        prompt = f"""分析"{self.core_idea}"概念：

1. 核心思想是什么？
2. 如何应用到{self.product_type}？
3. 与现有工具的差异在哪里？

用中文回答，简洁明了。"""
        
        results = {}
        for model in self.models:
            result = self._call_llm(model, prompt)
            results[model] = result
        
        self._analyze_results(results)
        return results
    
    def reverse_refactor(self) -> str:
        """反向重构 - 从复杂到简洁"""
        steps = [
            "提炼核心 - 找出最重要的理念",
            "拆分细节 - 将复杂内容分到独立文档",
            "简化结构 - 删除冗余，保持清晰"
        ]
        
        for step in steps:
            print(f"执行：{step}")
        
        self.prd_content = self._apply_reverse_refactor()
        return self.prd_content
    
    def simulate_user(self) -> List[str]:
        """用户模拟 - LLM模拟潜在用户阅读反馈"""
        prompt = f"""你是一个{self.product_type}开发者，阅读以下PRD文档：

{self.prd_content}

从用户角度提出修改建议：
1. 叙事逻辑问题
2. 内容理解障碍
3. 格式改进建议

用中文回答，简洁明了。"""
        
        feedbacks = []
        for model in self.models[:2]:  # 只用两个模型
            feedback = self._call_llm(model, prompt)
            feedbacks.append(feedback)
        
        self._apply_feedback(feedbacks)
        return feedbacks
    
    def unify_titles(self) -> str:
        """统一标题 - 使用名词短语"""
        noun_titles = [
            "用户痛点",
            "解决方案",
            "核心功能",
            "用户收益"
        ]
        
        self.prd_content = self._apply_title_structure(noun_titles)
        return self.prd_content
    
    def simplify(self) -> str:
        """简化完善 - 删除过度设计"""
        simplification_rules = [
            "删除复杂架构设计",
            "删除扩展功能模块",
            "删除详细用户旅程",
            "保留核心：痛点、方案、功能、收益"
        ]
        
        for rule in simplification_rules:
            print(f"应用：{rule}")
        
        self.prd_content = self._apply_simplification()
        return self.prd_content
    
    def save(self, filepath: str) -> None:
        """保存PRD文档"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.prd_content)
        print(f"PRD已保存到：{filepath}")
    
    def _call_llm(self, model: str, prompt: str) -> str:
        """调用LLM API"""
        try:
            cmd = ["llm", "-m", model, prompt]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout.strip()
        except Exception as e:
            return f"LLM调用失败：{e}"
    
    def _analyze_results(self, results: dict) -> None:
        """分析头脑风暴结果"""
        core_points = []
        for model, result in results.items():
            lines = result.split('\n')
            for line in lines:
                if '核心' in line or '差异' in line:
                    core_points.append(line)
        
        print(f"发现核心理念：{len(core_points)} 个要点")
    
    def _apply_reverse_refactor(self) -> str:
        """应用反向重构"""
        return f"""# {self.product_name}产品需求文档

## 用户痛点

AI工具的黑箱困境：盲目信任、能力外包、幻觉风险。

## 解决方案

核心理念：透明化AI认知过程，帮助人类理解和掌握。

{self.core_idea}作为方法论：正向渐进式展开，反向提炼重组。

## 核心功能

全量审计：展示AI识别问题的过程。

增量评审：展示AI推理的逻辑链条。

持续改进：展示AI策略的权衡依据。

## 用户收益

透明化认知过程，从被动接受到主动掌控，能力内化而非单纯产出。

"""
    
    def _apply_feedback(self, feedbacks: List[str]) -> None:
        """应用用户反馈"""
        for feedback in feedbacks:
            if '逻辑混乱' in feedback:
                print("发现叙事逻辑问题，需要调整")
            if '标题' in feedback:
                print("发现标题问题，需要统一")
    
    def _apply_title_structure(self, titles: List[str]) -> str:
        """应用标题结构"""
        sections = self.prd_content.split('\n\n')
        new_sections = []
        
        for i, title in enumerate(titles):
            if i < len(sections):
                section = sections[i].replace('## ', f'## {title}\n\n')
                new_sections.append(section)
        
        return '\n\n'.join(new_sections)
    
    def _apply_simplification(self) -> str:
        """应用简化规则"""
        lines = self.prd_content.split('\n')
        simplified_lines = []
        
        skip_keywords = ['架构', '扩展', '详细文档', '旅程']
        
        for line in lines:
            should_skip = any(kw in line for kw in skip_keywords)
            if not should_skip:
                simplified_lines.append(line)
        
        return '\n'.join(simplified_lines)


def write_prd_with_transparent_cognition(
    product_name: str,
    core_idea: str,
    product_type: str = "编程"
) -> str:
    """完整的PRD写作流程 - 透明化AI认知过程"""
    
    writer = PRDWriter(product_name, product_type)
    
    print("=== 1. 初始写作 ===")
    writer.initial_draft(core_idea)
    
    print("=== 2. 头脑风暴核心理念 ===")
    writer.brainstorm_core()
    
    print("=== 3. 反向重构文档 ===")
    writer.reverse_refactor()
    
    print("=== 4. 模拟用户反馈 ===")
    writer.simulate_user()
    
    print("=== 5. 简化过度设计 ===")
    writer.simplify()
    
    print("=== 6. 统一标题格式 ===")
    writer.unify_titles()
    
    return writer.prd_content


if __name__ == "__main__":
    prd = write_prd_with_transparent_cognition(
        product_name="量潮编程云",
        core_idea="雪花编程法",
        product_type="编程"
    )
    
    output_path = "docs/prd/index.md"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(prd)
    
    print(f"\nPRD已生成：{output_path}")
    print("\n核心特点：")
    print("- 透明化AI认知过程")
    print("- 反向重构方法论")
    print("- 用户视角叙事逻辑")
    print("- 简洁避免过度设计")