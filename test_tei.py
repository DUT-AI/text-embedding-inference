#!/usr/bin/env python3
"""
Test script kiểm tra Text Embeddings Inference (TEI) cho Tiếng Việt với API Key Authentication.
"""

import json
import urllib.request
import urllib.error

GATEWAY_URL = "http://localhost:8090"
API_KEY = "dutaiclb"

def post_json(url: str, data: dict, api_key: str = API_KEY):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

def test_gateway_health():
    print("=" * 65)
    print("1. Kiểm tra trạng thái Gateway & Endpoint tổng quan")
    print("=" * 65)
    try:
        req = urllib.request.Request(f"{GATEWAY_URL}/")
        with urllib.request.urlopen(req) as resp:
            info = json.loads(resp.read().decode("utf-8"))
            print("✅ Nginx Gateway hoạt động bình thường!")
            print(json.dumps(info, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Không thể kết nối tới Gateway tại {GATEWAY_URL}: {e}")
        return False
    return True

def test_api_key_security():
    print("\n" + "=" * 65)
    print("2. Kiểm thử Bảo mật API Key (Từ chối truy cập trái phép)")
    print("=" * 65)
    url = f"{GATEWAY_URL}/embed"
    payload = {"inputs": ["Kiểm tra bảo mật API Key"]}
    
    # Test 1: Không truyền API Key
    try:
        print("-> [Test 2.1] Gửi request KHÔNG có API Key...")
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req)
        print("❌ Lỗi: Server không chặn request thiếu API Key!")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✅ Chuẩn xác: Server trả về 401 Unauthorized khi thiếu API Key.")
        else:
            print(f"⚠️ Trả về mã lỗi: {e.code}")

    # Test 2: Truyền sai API Key
    try:
        print("-> [Test 2.2] Gửi request với API Key SAI ('wrong_key')...")
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": "Bearer wrong_key"})
        urllib.request.urlopen(req)
        print("❌ Lỗi: Server không chặn API Key sai!")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("✅ Chuẩn xác: Server từ chối 401 Unauthorized khi API Key không đúng.")
        else:
            print(f"⚠️ Trả về mã lỗi: {e.code}")

def test_vietnamese_embedding():
    print("\n" + "=" * 65)
    print("3. Kiểm tra TEI Embedding tiếng Việt (/embed) với API Key")
    print("=" * 65)
    
    sentences = [
        "Hà Nội là thủ đô của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam.",
        "Trí tuệ nhân tạo và mô hình ngôn ngữ lớn đang phát triển rất nhanh.",
        "Phở bò và bún chả là những món ăn truyền thống nổi tiếng của Việt Nam."
    ]
    
    url = f"{GATEWAY_URL}/embed"
    payload = {"inputs": sentences, "normalize": True}
    
    try:
        print(f"Gửi {len(sentences)} câu tiếng Việt tới: {url} (Header: Authorization Bearer)")
        embeddings = post_json(url, payload, api_key=API_KEY)
        
        print(f"✅ Tạo vector embedding thành công!")
        print(f" - Số lượng vector trả về: {len(embeddings)}")
        print(f" - Kích thước vector (dimension): {len(embeddings[0])}")
        print(f" - Mẫu 5 giá trị đầu tiên của vector 1: {embeddings[0][:5]}")
    except Exception as e:
        print(f"❌ Lỗi khi gọi Embedding: {e}")

def test_vietnamese_reranker():
    print("\n" + "=" * 65)
    print("4. Kiểm tra TEI Reranker tiếng Việt (/rerank) với API Key")
    print("=" * 65)
    
    query = "Thủ đô của Việt Nam là thành phố nào?"
    documents = [
        "Đà Nẵng là thành phố đáng sống với nhiều bãi biển đẹp.",
        "Hà Nội là thủ đô của Việt Nam từ năm 1945, nổi tiếng với 36 phố phường và hồ Hoàn Kiếm.",
        "Thành phố Hồ Chí Minh là trung tâm kinh tế tài chính lớn nhất cả nước.",
        "Việt Nam nằm ở khu vực Đông Nam Á, có bờ biển dài hơn 3260 km."
    ]
    
    url = f"{GATEWAY_URL}/rerank"
    payload = {
        "query": query,
        "texts": documents,
        "raw_scores": False,
        "return_text": True
    }
    
    try:
        print(f"Query: \"{query}\"")
        print(f"Đánh giá độ liên quan cho {len(documents)} đoạn văn bản...")
        results = post_json(url, payload, api_key=API_KEY)
        
        print(f"✅ Reranking thành công! Kết quả sắp xếp theo mức độ liên quan:")
        for rank, item in enumerate(results, start=1):
            idx = item["index"]
            score = item["score"]
            text = item.get("text", documents[idx])
            print(f"  [{rank}] Score: {score:.4f} | Index {idx}: \"{text}\"")
            
    except Exception as e:
        print(f"❌ Lỗi khi gọi Reranker: {e}")

def test_openai_compatible_endpoint():
    print("\n" + "=" * 65)
    print("5. Kiểm tra Endpoint tương thích OpenAI (/v1/embeddings)")
    print("=" * 65)
    
    url = f"{GATEWAY_URL}/v1/embeddings"
    payload = {
        "input": ["Xin chào, đây là câu kiểm tra qua chuẩn OpenAI format."],
        "model": "BAAI/bge-m3"
    }
    
    try:
        resp = post_json(url, payload, api_key=API_KEY)
        print(f"✅ Gọi thành công qua chuẩn OpenAI format!")
        print(f" - Model: {resp.get('model')}")
        print(f" - Kích thước vector: {len(resp['data'][0]['embedding'])}")
        print(f" - Total tokens: {resp.get('usage', {}).get('total_tokens')}")
    except Exception as e:
        print(f"❌ Lỗi khi gọi OpenAI-compatible endpoint: {e}")

if __name__ == "__main__":
    if test_gateway_health():
        test_api_key_security()
        test_vietnamese_embedding()
        test_vietnamese_reranker()
        test_openai_compatible_endpoint()
    print("\n" + "=" * 65)
    print("Hoàn tất kiểm thử.")
    print("=" * 65)
