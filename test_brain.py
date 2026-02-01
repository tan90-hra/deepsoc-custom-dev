from openai import OpenAI
import os

# 这里填你的 Key
api_key = "sk-65c32cee8b21420cb072b20ecf53e860" 

# 【关键尝试】加上 /v1 后缀，DeepSeek 对 OpenAI SDK 的兼容性通常需要这个
base_url = "https://api.deepseek.com/v1"

print(f"Testing connection to: {base_url} with Key: {api_key[:5]}...")

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helper."},
            {"role": "user", "content": "Reply 'OK' if you see this."}
        ]
    )
    print("\n✅ 成功! AI 回复:")
    print(response.choices[0].message.content)
except Exception as e:
    print("\n❌ 失败! 错误详情:")
    print(e)
