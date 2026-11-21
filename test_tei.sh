#!/usr/bin/env bash

GATEWAY_URL="http://localhost:8090"
API_KEY="dutaiclb"

# Hàm in JSON đẹp không phụ thuộc vào jq
pretty_print() {
  if command -v jq >/dev/null 2>&1; then
    jq .
  elif command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool 2>/dev/null || cat
  else
    cat
  fi
}

echo "============================================================"
echo "1. Kiểm tra Gateway Information (Public Endpoint)"
echo "============================================================"
curl -s "${GATEWAY_URL}/" | pretty_print
echo -e "\n"

echo "============================================================"
echo "2. Kiểm thử Bảo mật API Key (Từ chối khi không có Key)"
echo "============================================================"
echo "Gửi request KHÔNG có API Key (Kỳ vọng nhận 401 Unauthorized):"
curl -s -i -X POST "${GATEWAY_URL}/embed" \
  -H 'Content-Type: application/json' \
  -d '{"inputs": ["test"]}' | head -n 1
echo -e "\n"

echo "============================================================"
echo "3. Kiểm tra TEI Embedding tiếng Việt (/embed) với API Key"
echo "============================================================"
curl -s -X POST "${GATEWAY_URL}/embed" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": [
      "Hà Nội là thủ đô của Việt Nam.",
      "Mô hình ngôn ngữ lớn và trí tuệ nhân tạo."
    ],
    "normalize": true
  }' | pretty_print
echo -e "\n"

echo "============================================================"
echo "4. Kiểm tra TEI Reranking tiếng Việt (/rerank) với API Key"
echo "============================================================"
curl -s -X POST "${GATEWAY_URL}/rerank" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Thủ đô của Việt Nam là gì?",
    "texts": [
      "Đà Nẵng có nhiều bãi biển đẹp và cầu Rồng.",
      "Hà Nội là thủ đô của Việt Nam từ năm 1945.",
      "TP Hồ Chí Minh là trung tâm kinh tế sôi động."
    ],
    "return_text": true
  }' | pretty_print
echo -e "\n"

echo "============================================================"
echo "5. Kiểm tra OpenAI-compatible (/v1/embeddings) với API Key"
echo "============================================================"
curl -s -X POST "${GATEWAY_URL}/v1/embeddings" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "Học máy và tìm kiếm ngữ nghĩa.",
    "model": "BAAI/bge-m3"
  }' | pretty_print
echo -e "\n"
