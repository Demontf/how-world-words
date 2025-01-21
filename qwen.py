from openai import OpenAI
from large_text_handler import TranslationHandler
import re

qwen_model = "qwen-turbo-1101"  # qwen-turbo-latest
file_name = "mars"
max_output_tokens = 5000


def call_qwen(prompt, data, model, log_name):
    print('Sending to qwen translate....')
    client = OpenAI(
        api_key='',
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {'role': 'system', 'content': '你是一个翻译专家和大师,请完成英文到中文的翻译任务'},
                {'role': 'user', 'content': prompt+data}
            ],
        )
        #return completion.choices[0].message.content
        save_ch(log_name,completion.model_dump_json())
        # 解析 JSON 数据
        content = ""
        idx = 0
        # 遍历 choices，获取 message->content 的值并拼接
        for choice in completion.choices:
            idx+=1
            content += choice.message.content  # 拼接内容并加上空格分隔
        return content
    except Exception as e:
        print(e)

    return data
    
    

def save_ch(ch_file_name,data):
    try:
        with open(ch_file_name, 'w') as file:
            file.write(data)
        print("file saved to "+ch_file_name)
    except Exception as e:
            print(f"Error processing files: {e}")
            raise

def save_ch_append(ch_file_name,data):
    try:
        with open(ch_file_name, 'a') as file:
            file.write(data)
    except Exception as e:
            print(f"Error processing files: {e}")
            raise

# 读取文件并统计单词数量
def count_words_in_file(text):
    words = text.split()  # 使用空白字符（空格、换行符等）分割文本为单词
    return len(words)  # 返回单词数量
    
def count_hanzi(text):
    return len(re.findall(r'[\u4e00-\u9fff]', text))

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

    handler = TranslationHandler(max_tokens=max_output_tokens)

    # 准备翻译文本分段
    translation_requests = handler.process_text(english_text)

    # 这里需要实际的API调用逻辑
    idx = 0
    #translations = []
    print("文章分"+str(len(translation_requests))+"部分进行翻译")
    for request in translation_requests:
        print("输入英文："+str(count_words_in_file(request['text'])))
        # prompt
        # translate_prompt = f"""我给你提供英文文本，为了翻译更准确和流畅，同时提供了对应文本的上下文。上文的内容是:{request['previous_context']}
        # ,之后的部分内容是: {request['next_context']} . 当前位置: {request['position']}。 
        # 翻译要求1.中文和英文段落要对应,格式保持一致，2.仅返回对应文本的翻译内容，额外的文字都不需要.
        # 需翻译的英文如下：{request["text"]} """

        translate_prompt = f"""请将英文文本翻译成中文。 
        翻译要求1.中文和英文段落要对应,格式(如换行等)保持一致，2.仅返回对应文本的翻译内容，额外的文字都不需要. 3.涉及敏感和违规词汇请用**代替
        需翻译的英文如下: """
        
        save_ch(str(idx)+".prompt",translate_prompt+request["text"])
        result = call_qwen(translate_prompt,request["text"],qwen_model,str(idx)+".json")
        print("输出结果 result:"+str(count_hanzi(result)))
        #print(result)
        save_ch_append(file_name+"_ch.txt","\n"+result)
        #translations.append(result)
        idx +=1 
    
    # 合并结果
    #final_translation = handler.merge_translations(translations)
    #print(translation_requests)
    
    #save_ch(file_name+"_ch.txt",final_translation)







