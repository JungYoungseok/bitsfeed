import os
import json
import openai
import hashlib
from datetime import datetime
from pymongo.collection import Collection

openai.api_key = os.getenv("OPENAI_API_KEY")


def build_prompt(article):
    return f"""
{article['source']}에서 publish한 {article['title']} 기사 내용에 대해서 아래 내용에 맞춰서 정리 부탁해요.
1. 기사 핵심 내용을 300자 이내로 요약해 주세요.
2. 이 기사가 Observability 시장 혹은 한국 시장에 어떤 영향이 있는지 혹은 200자 내외로 정리해 주세요. 주식 판매 소식의 경우 Market cap 대비 몇 퍼센트인지만 알려주면 좋겠어요. 1% 이하일 경우 담백하게 비율만 간단히 언급해주세요.

응답 희망 포맷은 아래와 같아
{{
  "title": "...",
  "url": "...",
  "summary_ko": "...",
  "impact_ko": "..."
}}   """

def call_openai(prompt: str) -> dict:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        print("🔁 OpenAI raw content:", content)

        if not content:
            print("⚠️ OpenAI 응답이 비어있습니다.")
            return {}

        return json.loads(content)

    except json.JSONDecodeError as je:
        print("❌ JSON 파싱 실패:", je)
        print("🔎 OpenAI 응답:\n", content)
        return {}
    except Exception as e:
        print("❌ OpenAI 호출 실패:", e)
        return {}

def save_summary_to_mongo(collection: Collection, article_id: str, summary: dict):
    if not summary.get("summary_ko"):
        print("⚠️ 요약 필드가 없습니다. 저장하지 않습니다.")
        return

    doc = {
        "summary_ko": summary.get("summary_ko"),
        "impact_ko": summary.get("impact_ko", ""),
        "summary_generated_at": datetime.utcnow()
    }
    result = collection.update_one({"_id": article_id}, {"$set": doc})
    print(f"✅ Updated {article_id}: matched={result.matched_count}, modified={result.modified_count}")

