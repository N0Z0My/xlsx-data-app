import asyncio
from openai import OpenAI
import streamlit as st
from .logger import logger

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

async def evaluate_answer_with_gpt(question, options, user_answer):
    prompt = f"""
    問題: {question}
    選択肢: {options}
    ユーザーの回答: {user_answer}

    以下の手順でユーザーの回答を評価し、必ず指定された形式で回答してください：
    1. 問題文と選択肢から最も適切な選択肢を１つ選んでください。
    2. ユーザーの回答が最も適切な選択肢と一致するか評価してください。
    3. 以下のフォーマットを厳密に守って回答してください：

    RESULT:[CORRECT] または RESULT:[INCORRECT]
    
    あなたの回答: {user_answer}
    
    正解: [適切な選択肢]
    
    解説: [正解の短い解説]
    """

    try:
        logger.info(f"GPT評価開始 - 問題: {question}, ユーザー回答: {user_answer}")
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4",
            temperature=0.4,
            messages=[
                {"role": "system", "content": "あなたは海外旅行の豊富な知識を持っていて、ユーザーの回答を評価する優秀な採点者です。必ず指定された形式で回答してください。"},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_response = response.choices[0].message.content
        logger.info(f"GPT評価完了 - 結果: {gpt_response}")
        return gpt_response
    except Exception as e:
        error_msg = f"エラーが発生しました: {str(e)}"
        logger.error(error_msg)
        return error_msg