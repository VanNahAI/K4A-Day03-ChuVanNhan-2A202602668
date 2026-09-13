"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import re
import sys
import json
import time
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, ".env"))


class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        # Tách phần câu hỏi gốc khỏi lịch sử thực thi để tránh nhầm từ khóa
        user_query_part = prompt_lower.split("lịch sử")[0] if "yêu cầu ban đầu của người dùng:" in prompt_lower else prompt_lower

        # Nếu đã có lịch sử thực thi (bước 2 trở đi)
        if "[bước" in prompt_lower or "kết quả observation" in prompt_lower:
            if "not_found" in prompt_lower:
                return {
                    "type": "text",
                    "content": "Rất tiếc, hệ thống không tìm thấy dữ liệu sinh viên trong cơ sở dữ liệu học vụ VinUni. Bạn vui lòng kiểm tra lại mã số sinh viên.",
                    "thought": "Dữ liệu sinh viên không tồn tại trong hệ thống (NOT_FOUND). Trả lời thông báo lịch sự, không bịa đặt thông tin (Anti-Hallucination)."
                }
            elif "academic_query" in prompt_lower and "đặt lịch" in user_query_part and "schedule_appointment" not in prompt_lower:
                # TC04: Sau khi tra cứu xong, tiếp tục đặt lịch (multi-step)
                return {
                    "type": "tool_call",
                    "tool_name": "schedule_appointment",
                    "arguments": {
                        "student_id": "SV2026001",
                        "datetime_str": "09:00 20/09/2026",
                        "advisor_name": "PGS.TS Nguyễn Văn A"
                    },
                    "thought": "Đã có thông tin Cố vấn học tập từ bước tra cứu. Tiếp tục gọi tool schedule_appointment để đặt lịch hẹn."
                }
            elif "schedule_appointment" in prompt_lower:
                return {
                    "type": "text",
                    "content": "Đã hoàn tất quy trình: Đã tra cứu cố vấn học tập PGS.TS Nguyễn Văn A và đặt lịch hẹn thành công cho sinh viên SV2026001 vào lúc 09:00 ngày 20/09/2026 (Mã booking: BK-SV2026001-99).",
                    "thought": "Đã hoàn thành toàn bộ các bước suy luận và hành động. Tổng hợp kết luận cuối cùng cho sinh viên."
                }
            elif "academic_query" in prompt_lower and ("nguyễn văn an" in prompt_lower or "sv2026001" in prompt_lower):
                return {
                    "type": "text",
                    "content": "Thông tin học vụ sinh viên SV2026001 (Nguyễn Văn An): Lớp AI-K4, GPA: 3.85, Email: an.nv@vinuni.edu.vn, Trạng thái: Đang học, Cố vấn học tập: PGS.TS Nguyễn Văn A.",
                    "thought": "Đã nhận được dữ liệu học vụ từ Observation. Tổng hợp câu trả lời cho sinh viên."
                }
            else:
                return {
                    "type": "text",
                    "content": "Đã hoàn tất xử lý yêu cầu và tổng hợp thông tin từ hệ thống học vụ VinUni.",
                    "thought": "Tổng hợp kết quả từ Observation để trả lời người dùng."
                }

        # Lượt đầu tiên: Phân tích intent từ câu hỏi người dùng
        if "sv9999999" in user_query_part:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": "SV9999999"},
                "thought": "Người dùng yêu cầu tra cứu thông tin sinh viên SV9999999. Tôi sẽ gọi tool academic_query."
            }
        elif "đặt lịch" in user_query_part and "tra cứu" not in user_query_part:
            return {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {
                    "student_id": "SV2026001",
                    "datetime_str": "14:00 15/09/2026",
                    "advisor_name": "PGS.TS Nguyễn Văn A"
                },
                "thought": "Người dùng yêu cầu đặt lịch hẹn tư vấn cho sinh viên SV2026001. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "sv2026001" in user_query_part or "tra cứu" in user_query_part:
            return {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": "SV2026001"},
                "thought": "Yêu cầu tra cứu thông tin học vụ của sinh viên SV2026001. Tôi sẽ gọi tool academic_query."
            }
        else:
            return {
                "type": "text",
                "content": "Xin chào! Quy chế học vụ Đại học VinUni yêu cầu sinh viên tích lũy tối thiểu 120 tín chỉ và duy trì GPA từ 2.0 trở lên để đủ điều kiện tốt nghiệp. Bạn có cần hỗ trợ tra cứu thông tin cụ thể nào không?",
                "thought": "Câu hỏi chung về quy chế học vụ, trả lời trực tiếp không cần gọi Tool."
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-2.5-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        for attempt in range(5):
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.api_key)

                function_declarations = [
                    {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                    for tool in tools_schema
                    if tool.get("name") and tool.get("parameters")
                ]

                config = types.GenerateContentConfig(
                    system_instruction=system_prompt if system_prompt else None,
                    tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                    temperature=0.2
                )

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )

                if response.function_calls:
                    call = response.function_calls[0]
                    args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                    return {
                        "type": "tool_call",
                        "tool_name": call.name,
                        "arguments": args,
                        "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                    }
                else:
                    return {
                        "type": "text",
                        "content": response.text or "",
                        "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                    }

            except Exception as e:
                err_str = str(e)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < 4:
                    wait_time = 30
                    match = re.search(r'retry in (\d+(?:\.\d+)?)s', err_str)
                    if match:
                        wait_time = int(float(match.group(1))) + 5
                    backoff_wait = min(wait_time * (2 ** attempt), 120)
                    print(f"⏳ [Gemini API Rate Limit 429] Lần thử {attempt+1}/5: Tạm dừng {backoff_wait}s...")
                    time.sleep(backoff_wait)
                    continue
                print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({err_str}). Tự động fallback về Mock.")
                return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                }
                for tool in tools_schema if tool.get("name")
            ]

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}"
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ)."
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
