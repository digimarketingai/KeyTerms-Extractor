"""
KeyTerms Extractor - 术语提取器
A bilingual key terms extraction tool with translation and definitions.
双语术语提取工具，提供翻译和定义。

Author: DigiMarketingAI
GitHub: https://github.com/digimarketingai
"""

import os
import re
import json
import csv
from typing import Optional, List, Dict

try:
    from mistralai import Mistral
except ImportError:
    raise ImportError("Please install mistralai: pip install mistralai")


class KeyTermsExtractor:
    """
    A class to extract key terms from text and provide translations/definitions.
    從文本中提取關鍵術語並提供翻譯/定義的工具類。
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-medium-latest"):
        """
        Initialize the KeyTermsExtractor.
        初始化術語提取器。
        
        Args:
            api_key: Mistral API key. If None, will try to get from environment variable.
                     Mistral API 金鑰。如果為 None，將嘗試從環境變數獲取。
            model: Mistral model to use.
                   使用的 Mistral 模型。
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Set MISTRAL_API_KEY environment variable or pass api_key parameter.\n"
                "需要 API 金鑰。請設置 MISTRAL_API_KEY 環境變數或傳入 api_key 參數。"
            )
        
        self.model = model
        self.client = Mistral(api_key=self.api_key)
    
    def _is_relevant_prompt(self, custom_prompt: str) -> bool:
        """
        Check if the custom prompt is relevant to term extraction.
        檢查自定義提示是否與術語提取相關。
        """
        relevance_keywords = [
            # English keywords
            "term", "extract", "focus", "only", "include", "exclude", "type",
            "category", "field", "domain", "technical", "medical", "legal",
            "scientific", "business", "ignore", "skip", "important", "key", 
            "specific", "related", "terminology", "vocabulary", "jargon",
            # Chinese keywords (Traditional & Simplified)
            "詞", "词", "術語", "术语", "提取", "專業", "专业", "領域", "领域",
            "技術", "技术", "醫學", "医学", "法律", "科學", "科学", "商業", "商业",
            "忽略", "重要", "關鍵", "关键", "特定", "相關", "相关", "類型", "类型"
        ]
        
        return any(keyword.lower() in custom_prompt.lower() for keyword in relevance_keywords)
    
    def extract(
        self, 
        text: str, 
        custom_prompt: str = "",
        output_format: str = "dict"
    ) -> Optional[List[Dict]]:
        """
        Extract key terms from text with translations and definitions.
        從文本中提取關鍵術語，並提供翻譯和定義。
        
        Args:
            text: The input text to analyze.
                  要分析的輸入文本。
            custom_prompt: Optional custom instructions for term extraction.
                          可選的自定義術語提取指令。
            output_format: Output format - "dict", "json", or "markdown".
                          輸出格式 - "dict"、"json" 或 "markdown"。
        
        Returns:
            List of dictionaries containing extracted terms, or None if extraction fails.
            包含提取術語的字典列表，如果提取失敗則返回 None。
        """
        
        if not text or not text.strip():
            print("⚠️ Empty text provided. 提供的文本為空。")
            return None
        
        # Build the extraction prompt
        base_instruction = """You are a professional terminology extractor and translator. 
Analyze the following text and extract all key terms (technical terms, domain-specific vocabulary, 
important concepts, proper nouns, and specialized terminology).

For each term, provide:
1. The original term
2. Translation (English if the term is in Chinese/other language, Traditional Chinese 繁體中文 if the term is in English)
3. A clear, concise definition (provide in both English and Traditional Chinese)

Format your response as a JSON array with objects containing:
- "term": the original term
- "translation": the translation
- "definition_en": definition in English
- "definition_zh": definition in Traditional Chinese (繁體中文)
- "category": the type of term (e.g., "technical", "concept", "proper noun", "domain-specific", etc.)
"""

        # Add custom prompt if provided and relevant
        custom_instruction = ""
        if custom_prompt and custom_prompt.strip():
            if self._is_relevant_prompt(custom_prompt):
                custom_instruction = f"\n\nAdditional Instructions 額外指令: {custom_prompt}"
            else:
                print(f"ℹ️ Custom prompt ignored (not related to term extraction): {custom_prompt[:50]}...")
                print(f"ℹ️ 自定義提示已忽略（與術語提取無關）：{custom_prompt[:50]}...")

        # Construct the full prompt
        full_prompt = f"""{base_instruction}{custom_instruction}

TEXT TO ANALYZE 要分析的文本:
\"\"\"
{text}
\"\"\"

Please extract all key terms and respond ONLY with a valid JSON array. No additional text.
請提取所有關鍵術語，僅回應有效的 JSON 陣列，不要有其他文字。"""

        try:
            # Call Mistral API
            chat_response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt,
                    }
                ]
            )
            
            response_text = chat_response.choices[0].message.content
            
            # Parse JSON from the response
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            if json_match:
                terms = json.loads(json_match.group())
                
                # Handle output format
                if output_format == "json":
                    return json.dumps(terms, ensure_ascii=False, indent=2)
                elif output_format == "markdown":
                    return self._to_markdown(terms)
                else:
                    return terms
            else:
                print("⚠️ Could not parse JSON response. 無法解析 JSON 回應。")
                print(f"Raw response 原始回應: {response_text}")
                return None
                
        except Exception as e:
            print(f"❌ Error 錯誤: {str(e)}")
            return None
    
    def _to_markdown(self, terms: List[Dict]) -> str:
        """Convert terms to markdown format. 將術語轉換為 Markdown 格式。"""
        if not terms:
            return "No terms extracted. 未提取到術語。"
        
        md = "# Extracted Key Terms 提取的關鍵術語\n\n"
        md += f"**Total terms 術語總數: {len(terms)}**\n\n"
        md += "---\n\n"
        
        for i, term in enumerate(terms, 1):
            md += f"## {i}. {term.get('term', 'N/A')}\n\n"
            md += f"**Translation 翻譯:** {term.get('translation', 'N/A')}\n\n"
            md += f"**Category 類別:** {term.get('category', 'N/A')}\n\n"
            md += f"**Definition (EN):** {term.get('definition_en', term.get('definition', 'N/A'))}\n\n"
            md += f"**定義 (中文):** {term.get('definition_zh', 'N/A')}\n\n"
            md += "---\n\n"
        
        return md
    
    def extract_from_file(
        self, 
        file_path: str, 
        custom_prompt: str = "",
        encoding: str = "utf-8"
    ) -> Optional[List[Dict]]:
        """
        Extract key terms from a text file.
        從文本文件中提取關鍵術語。
        
        Args:
            file_path: Path to the text file.
                      文本文件的路徑。
            custom_prompt: Optional custom instructions.
                          可選的自定義指令。
            encoding: File encoding.
                     文件編碼。
        
        Returns:
            List of extracted terms.
            提取的術語列表。
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            return self.extract(text, custom_prompt)
        except UnicodeDecodeError:
            # Try alternative encodings
            for enc in ['gbk', 'big5', 'utf-16', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        text = f.read()
                    return self.extract(text, custom_prompt)
                except UnicodeDecodeError:
                    continue
            print(f"❌ Could not decode file. 無法解碼文件。")
            return None
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}. 找不到文件：{file_path}")
            return None
    
    def save_to_csv(
        self, 
        terms: List[Dict], 
        output_path: str = "extracted_terms.csv"
    ) -> bool:
        """
        Save extracted terms to a CSV file.
        將提取的術語保存到 CSV 文件。
        
        Args:
            terms: List of extracted terms.
                  提取的術語列表。
            output_path: Output file path.
                        輸出文件路徑。
        
        Returns:
            True if successful, False otherwise.
            成功返回 True，否則返回 False。
        """
        if not terms:
            print("⚠️ No terms to save. 沒有術語可保存。")
            return False
        
        try:
            fieldnames = ['term', 'translation', 'definition_en', 'definition_zh', 'category']
            
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                
                for term in terms:
                    # Handle both old and new format
                    row = {
                        'term': term.get('term', ''),
                        'translation': term.get('translation', ''),
                        'definition_en': term.get('definition_en', term.get('definition', '')),
                        'definition_zh': term.get('definition_zh', ''),
                        'category': term.get('category', '')
                    }
                    writer.writerow(row)
            
            print(f"✅ Saved to {output_path}. 已保存至 {output_path}。")
            return True
            
        except Exception as e:
            print(f"❌ Error saving file 保存文件錯誤: {str(e)}")
            return False
    
    def display(self, terms: List[Dict]) -> None:
        """
        Display extracted terms in a formatted way.
        以格式化方式顯示提取的術語。
        """
        if not terms:
            print("No terms to display. 沒有術語可顯示。")
            return
        
        print("\n" + "="*70)
        print("📚 EXTRACTED KEY TERMS 提取的關鍵術語")
        print("="*70)
        
        for i, term in enumerate(terms, 1):
            print(f"\n{i}. 【{term.get('term', 'N/A')}】")
            print(f"   📖 Translation 翻譯: {term.get('translation', 'N/A')}")
            print(f"   📝 Definition (EN): {term.get('definition_en', term.get('definition', 'N/A'))}")
            print(f"   📝 定義 (中文): {term.get('definition_zh', 'N/A')}")
            print(f"   🏷️  Category 類別: {term.get('category', 'N/A')}")
            print("-"*50)
        
        print(f"\n✅ Total terms extracted 術語總數: {len(terms)}")


# Convenience function for quick extraction
def extract_terms(
    text: str, 
    api_key: Optional[str] = None, 
    custom_prompt: str = ""
) -> Optional[List[Dict]]:
    """
    Quick function to extract terms from text.
    快速從文本中提取術語的函數。
    
    Args:
        text: Text to analyze. 要分析的文本。
        api_key: Mistral API key. Mistral API 金鑰。
        custom_prompt: Custom extraction instructions. 自定義提取指令。
    
    Returns:
        List of extracted terms. 提取的術語列表。
    
    Example 範例:
        >>> terms = extract_terms("Machine learning is a subset of AI.", api_key="your-key")
        >>> print(terms)
    """
    extractor = KeyTermsExtractor(api_key=api_key)
    return extractor.extract(text, custom_prompt)


if __name__ == "__main__":
    # Demo usage
    print("KeyTerms Extractor - 術語提取器")
    print("="*40)
    print("Import this module and use KeyTermsExtractor class or extract_terms function.")
    print("導入此模組並使用 KeyTermsExtractor 類或 extract_terms 函數。")
    print("\nExample 範例:")
    print('  from keyterms_extractor import KeyTermsExtractor')
    print('  extractor = KeyTermsExtractor(api_key="your-api-key")')
    print('  terms = extractor.extract("Your text here...")')
    print('  extractor.display(terms)')
