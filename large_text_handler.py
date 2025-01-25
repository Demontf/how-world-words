import re
from typing import List, Dict
import json

class TranslationHandler:
    def __init__(self, max_tokens: int = 7000):
        self.max_tokens = max_tokens
        
    def split_text(self, text: str) -> List[str]:
        """
        智能分割文本,确保上下文的完整性
        """
        # 首先按段落分割
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # 估算token数量(简单估算:英文按空格分词,中文按字符计数)
            estimated_tokens = len(re.findall(r'\s+', para)) + len(re.findall(r'[\u4e00-\u9fff]', para))
            
            if estimated_tokens > self.max_tokens:
                # 如果单个段落超过限制,按句子分割
                sentences = re.split(r'([.!?。！？]+)', para)
                temp_chunk = ""
                
                for i in range(0, len(sentences), 2):
                    if i + 1 < len(sentences):
                        sentence = sentences[i] + sentences[i+1]
                    else:
                        sentence = sentences[i]
                        
                    if len(temp_chunk) + len(sentence) < self.max_tokens:
                        temp_chunk += sentence
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = sentence
                
                if temp_chunk:
                    chunks.append(temp_chunk)
            else:
                # 检查当前chunk加上新段落是否超过限制
                if len(current_chunk) + len(para) + 1 < self.max_tokens:
                    current_chunk += ("\n" if current_chunk else "") + para
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def add_context(self, chunks: List[str]) -> List[Dict]:
        """
        为每个文本块添加上下文信息
        """
        requests = []
        for i, chunk in enumerate(chunks):
            context = {
                "text": chunk,
                "position": f"Part {i+1} of {len(chunks)}",
                "previous_context": chunks[i-1][-200:] if i > 0 else "",
                "next_context": chunks[i+1][:200] if i < len(chunks)-1 else ""
            }
            requests.append(context)
        return requests
    
    def merge_translations(self, translations: List[str]) -> str:
        """
        合并翻译结果
        """
        return "\n****\n".join(translations)
    
    def process_text(self, text: str) -> List[Dict]:
        """
        处理整个文本并准备翻译请求
        """
        chunks = self.split_text(text)
        return self.add_context(chunks)

# 使用示例
def example_usage():
    handler = TranslationHandler(max_tokens=7000)
    english_text = ''
    with open('mars.txt', 'r', encoding='utf-8') as f:
            english_text = f.read()
    
    
    # 准备翻译请求
    translation_requests = handler.process_text(english_text)
    
    # 这里需要实现实际的API调用逻辑
    translations = []
    for request in translation_requests:
        # 示例API调用格式
        # api_request = {
        #     "text": request["text"],
        #     "system_prompt": f"""Please translate the following text to Chinese. 
        #     This is {request['position']}. 
        #     Previous context: {request['previous_context']}
        #     Next context: {request['next_context']}"""
        # }
        translations.append(request["text"])
    #     # translations.append(call_translation_api(api_request))
    
    # # 合并结果
    # final_translation = handler.merge_translations(translations)
    # print(translation_requests)
    with open("test.txt", 'w') as file:
            file.write("\n".join(translations))



