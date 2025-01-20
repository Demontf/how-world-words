from openai import OpenAI
from large_text_handler import TranslationHandler

qwen_model = "qwen-turbo-1101"  # qwen-turbo-latest
file_name = "mars"
max_output_tokens = 1000


def call_qwen(prompt, model, data):
    print('Sending to qwen translate....')
    client = OpenAI(
        api_key='',
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': '你是一个翻译专家和大师,请完成英文到中文的翻译任务'},
            {'role': 'user', 'content': prompt + data}
        ],
    )
    
    #return completion.choices[0].message.content
    # 解析 JSON 数据
    save_ch(file_name+".json",completion.model_dump_json())
    content = ""
    idx = 0
    # 遍历 choices，获取 message->content 的值并拼接
    for choice in completion.choices:
        print('process idx:'+ str(idx))
        idx+=1
        content += choice.message.content  # 拼接内容并加上空格分隔
    return content

def save_ch(ch_file_name,data):
    try:
        with open(ch_file_name, 'a') as file:
            file.write(data)
        print("file saved to "+ch_file_name)
    except Exception as e:
            print(f"Error processing files: {e}")
            raise

# 读取文件并统计单词数量
def count_words_in_file(text):
    words = text.split()  # 使用空白字符（空格、换行符等）分割文本为单词
    return len(words)  # 返回单词数量
    


def load_eng_text():

    try:
        with open(file_name+'.txt', 'r', encoding='utf-8') as f:
            english_text = f.read()
            text_len = count_words_in_file(english_text)
            print('Read file Success: total has '+str(text_len)+ ' words')
            return english_text
    except Exception as e:
            print(f"Error processing files: {e}")
            raise


if __name__ == '__main__':

    english_text = load_eng_text()

    #main()
    handler = TranslationHandler(max_tokens=max_output_tokens)

    # 准备翻译请求
    translation_requests = handler.process_text(english_text)

    # 这里需要实际的API调用逻辑
    idx = 0
    translations = []
    for request in translation_requests:
        if idx > 2:
            break
        print("输入英文："+str(count_words_in_file(request['text'])))
        # prompt
        translate_prompt = f"""我给你提供英文文本，为了翻译更准确和流畅，提供了对应文本的上下文。之前的内容是:{request['previous_context']}
        ,之后的部分内容是: {request['next_context']} . 当前位置: {request['position']}。 
        翻译要求1.段落要对应，2.仅返回对应文本的翻译内容，额外的文字都不需要, 例如'好的，以下是您提供的英文段落的中文翻译'，
        需翻译的英文如下：{request["text"]} """
        
        #print(translate_prompt)
        result = call_qwen(translate_prompt,qwen_model,"")
        print("输入结果 result:"+str(count_words_in_file(result)))
        #print(result)
        translations.append(result)
        idx+=1
    
    # 合并结果
    final_translation = handler.merge_translations(translations)
    #print(translation_requests)
    
    save_ch(file_name+"_ch.txt",final_translation)







