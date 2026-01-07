"""
KeyTerms Extractor - Gradio Web Interface
術語提取器 - Gradio 網頁介面

Run with: python app.py
Or in Colab: Simply run this file
"""

import os
import gradio as gr
from keyterms_extractor import KeyTermsExtractor
import json
import tempfile
import csv

# Global extractor instance
extractor = None

def initialize_extractor(api_key: str) -> str:
    """Initialize the extractor with API key."""
    global extractor
    try:
        if not api_key or not api_key.strip():
            return "❌ Please enter your Mistral API key. 請輸入您的 Mistral API 金鑰。"
        
        extractor = KeyTermsExtractor(api_key=api_key.strip())
        return "✅ API key validated successfully! 成功驗證 API 金鑰！"
    except Exception as e:
        return f"❌ Error 錯誤: {str(e)}"


def process_text(
    text: str, 
    custom_prompt: str,
    output_format: str
) -> tuple:
    """Process text and extract terms."""
    global extractor
    
    if extractor is None:
        return "❌ Please set your API key first. 請先設置您的 API 金鑰。", None, None
    
    if not text or not text.strip():
        return "❌ Please enter text to analyze. 請輸入要分析的文本。", None, None
    
    try:
        # Extract terms
        terms = extractor.extract(text, custom_prompt)
        
        if not terms:
            return "❌ No terms extracted. Please try different text. 未提取到術語，請嘗試不同的文本。", None, None
        
        # Format output based on selection
        if output_format == "Markdown 表格":
            output = extractor._to_markdown(terms)
        elif output_format == "JSON":
            output = json.dumps(terms, ensure_ascii=False, indent=2)
        else:  # Table format
            output = format_as_table(terms)
        
        # Create downloadable CSV
        csv_path = create_csv_file(terms)
        
        # Create summary
        summary = f"✅ Successfully extracted {len(terms)} terms. 成功提取 {len(terms)} 個術語。"
        
        return output, csv_path, summary
        
    except Exception as e:
        return f"❌ Error 錯誤: {str(e)}", None, None


def process_file(
    file,
    custom_prompt: str,
    output_format: str
) -> tuple:
    """Process uploaded file and extract terms."""
    global extractor
    
    if extractor is None:
        return "❌ Please set your API key first. 請先設置您的 API 金鑰。", None, None
    
    if file is None:
        return "❌ Please upload a file. 請上傳文件。", None, None
    
    try:
        # Read file content
        with open(file.name, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(file.name, 'r', encoding='gbk') as f:
                text = f.read()
        except:
            try:
                with open(file.name, 'r', encoding='big5') as f:
                    text = f.read()
            except:
                return "❌ Could not read file encoding. 無法讀取文件編碼。", None, None
    
    return process_text(text, custom_prompt, output_format)


def format_as_table(terms: list) -> str:
    """Format terms as a readable table."""
    if not terms:
        return "No terms found."
    
    output = "📚 EXTRACTED KEY TERMS 提取的關鍵術語\n"
    output += "=" * 70 + "\n\n"
    
    for i, term in enumerate(terms, 1):
        output += f"【{i}】 {term.get('term', 'N/A')}\n"
        output += f"    📖 Translation 翻譯: {term.get('translation', 'N/A')}\n"
        output += f"    📝 Definition (EN): {term.get('definition_en', term.get('definition', 'N/A'))}\n"
        output += f"    📝 定義 (中文): {term.get('definition_zh', 'N/A')}\n"
        output += f"    🏷️  Category 類別: {term.get('category', 'N/A')}\n"
        output += "-" * 50 + "\n"
    
    output += f"\n✅ Total 總計: {len(terms)} terms 術語"
    return output


def create_csv_file(terms: list) -> str:
    """Create a temporary CSV file for download."""
    if not terms:
        return None
    
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.csv', 
        delete=False, 
        encoding='utf-8-sig',
        newline=''
    )
    
    fieldnames = ['term', 'translation', 'definition_en', 'definition_zh', 'category']
    writer = csv.DictWriter(temp_file, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    
    for term in terms:
        row = {
            'term': term.get('term', ''),
            'translation': term.get('translation', ''),
            'definition_en': term.get('definition_en', term.get('definition', '')),
            'definition_zh': term.get('definition_zh', ''),
            'category': term.get('category', '')
        }
        writer.writerow(row)
    
    temp_file.close()
    return temp_file.name


# Create Gradio Interface
def create_interface():
    """Create and return the Gradio interface."""
    
    with gr.Blocks(
        title="KeyTerms Extractor 術語提取器",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown("""
        # 🔤 KeyTerms Extractor 術語提取器
        
        Extract key terms from any text with translations and definitions.
        從任何文本中提取關鍵術語，並提供翻譯和定義。
        
        **Supports 支援:** English ↔ Traditional Chinese (繁體中文) translation
        """)
        
        # API Key Section
        with gr.Accordion("🔑 API Key Settings API 金鑰設置", open=True):
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="Mistral API Key",
                    placeholder="Enter your Mistral API key here... 在此輸入您的 Mistral API 金鑰...",
                    type="password",
                    scale=4
                )
                validate_btn = gr.Button("Validate 驗證", scale=1)
            
            api_status = gr.Textbox(
                label="Status 狀態",
                interactive=False
            )
        
        validate_btn.click(
            fn=initialize_extractor,
            inputs=[api_key_input],
            outputs=[api_status]
        )
        
        gr.Markdown("---")
        
        # Input Section
        with gr.Tab("📝 Text Input 文本輸入"):
            text_input = gr.Textbox(
                label="Enter text to analyze 輸入要分析的文本",
                placeholder="Paste your text here... 在此貼上您的文本...",
                lines=10
            )
        
        with gr.Tab("📁 File Upload 文件上傳"):
            file_input = gr.File(
                label="Upload a text file (.txt) 上傳文本文件",
                file_types=[".txt", ".md", ".text"]
            )
        
        # Options Section
        with gr.Row():
            custom_prompt = gr.Textbox(
                label="Custom Instructions (Optional) 自定義指令（可選）",
                placeholder="e.g., 'Focus on medical terms' 例如：'只提取醫學術語'",
                scale=3
            )
            output_format = gr.Dropdown(
                choices=["Table 表格", "Markdown 表格", "JSON"],
                value="Table 表格",
                label="Output Format 輸出格式",
                scale=1
            )
        
        # Action Buttons
        with gr.Row():
            extract_text_btn = gr.Button("🔍 Extract from Text 從文本提取", variant="primary")
            extract_file_btn = gr.Button("📁 Extract from File 從文件提取", variant="primary")
            clear_btn = gr.Button("🗑️ Clear 清除")
        
        # Output Section
        status_output = gr.Textbox(label="Status 狀態", interactive=False)
        
        result_output = gr.Textbox(
            label="Extracted Terms 提取的術語",
            lines=20,
            interactive=False
        )
        
        csv_download = gr.File(label="📥 Download CSV 下載 CSV")
        
        # Event handlers
        extract_text_btn.click(
            fn=process_text,
            inputs=[text_input, custom_prompt, output_format],
            outputs=[result_output, csv_download, status_output]
        )
        
        extract_file_btn.click(
            fn=process_file,
            inputs=[file_input, custom_prompt, output_format],
            outputs=[result_output, csv_download, status_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", None, ""),
            outputs=[result_output, csv_download, status_output]
        )
        
        # Examples
        gr.Markdown("---")
        gr.Markdown("### 💡 Example Custom Instructions 自定義指令範例")
        gr.Examples(
            examples=[
                ["Focus only on technical IT terms 只關注技術 IT 術語"],
                ["Extract medical terminology 提取醫學術語"],
                ["Only extract proper nouns and company names 只提取專有名詞和公司名稱"],
                ["Focus on legal terms 專注於法律術語"],
                ["Extract business and finance terms 提取商業和金融術語"],
            ],
            inputs=[custom_prompt]
        )
        
        gr.Markdown("""
        ---
        ### 📖 How to Use 使用方法
        
        1. **Enter API Key 輸入 API 金鑰:** Get your key from [Mistral AI](https://console.mistral.ai/)
        2. **Input Text 輸入文本:** Paste text or upload a file
        3. **Custom Instructions 自定義指令:** (Optional) Specify what types of terms to extract
        4. **Extract 提取:** Click the extract button and wait for results
        5. **Download 下載:** Download the results as CSV
        
        ---
        Made with ❤️ by [DigiMarketingAI](https://github.com/digimarketingai)
        """)
    
    return demo


# Main entry point
if __name__ == "__main__":
    # Check for API key in environment
    if os.environ.get("MISTRAL_API_KEY"):
        extractor = KeyTermsExtractor()
        print("✅ API key loaded from environment variable.")
    
    # Create and launch interface
    demo = create_interface()
    demo.launch(share=True)
