# 🚀 Triển Khai Text Embeddings Inference (TEI) cho Tiếng Việt

Dự án này cấu hình và triển khai hệ thống **Hugging Face Text Embeddings Inference (TEI)** phục vụ 2 mô hình tối ưu cho tiếng Việt:
1. **Embedding Model**: `BAAI/bge-m3` (1024 dims, context 8192 tokens, SOTA đa ngôn ngữ & tiếng Việt).
2. **Reranker Model**: `BAAI/bge-reranker-v2-m3` (Cross-encoder reranker SOTA cho tiếng Việt).
3. **Nginx API Gateway**: Hợp nhất toàn bộ các endpoint về **1 cổng duy nhất (`8090`)**.

---

## 🏛️ Kiến Trúc Hệ Thống

```
                     ┌──────────────────────────────────────────────┐
                     │         Client / RAG App / Python            │
                     └──────────────────────┬───────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          Nginx Gateway (Port 8090)           │
                     └──────────────┬────────────────┬──────────────┘
                                    │                │
            POST /embed             │                │   POST /rerank
            POST /v1/embeddings     │                │   POST /v1/rerank
                                    ▼                ▼
                     ┌────────────────────┐    ┌────────────────────┐
                     │   tei-embedding    │    │    tei-reranker    │
                     │    (Port 8082)     │    │    (Port 8083)     │
                     │    BAAI/bge-m3     │    │bge-reranker-v2-m3  │
                     └─────────┬──────────┘    └─────────┬──────────┘
                               │                         │
                               └────────────┬────────────┘
                                            ▼
                                  ./data (Shared Cache)
```

---

## 📋 Danh Sách Endpoint

| Service | Đường dẫn qua Gateway (Port 8090) | Port gốc (Direct) | Mô tả |
| :--- | :--- | :--- | :--- |
| **Gateway Info** | `GET http://localhost:8090/` | - | Danh sách tất cả endpoint đang hoạt động |
| **Embedding** | `POST http://localhost:8090/embed` | `8082` | Endpoint vector embedding chuẩn TEI |
| **Embedding (OpenAI)** | `POST http://localhost:8090/v1/embeddings` | `8082` | Chuẩn OpenAI (dùng với SDK OpenAI / LangChain) |
| **Reranking** | `POST http://localhost:8090/rerank` | `8083` | Endpoint cross-encoder reranking |
| **Health Check** | `GET http://localhost:8090/health/embedding`<br>`GET http://localhost:8090/health/rerank` | `8082`<br>`8083` | Kiểm tra trạng thái sẵn sàng của service |

---

## ⚡ Hướng Dẫn Khởi Động

### 1. Khởi động chế độ CPU (Mặc định)
Phù hợp với mọi máy chủ/laptop không có GPU NVIDIA:
```bash
docker compose up -d
```

### 2. Khởi động chế độ NVIDIA GPU (Tăng tốc tối đa)
Nếu máy chủ có GPU NVIDIA và đã cài `nvidia-container-toolkit`:
```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### 3. Xem logs tiến trình tải model
```bash
# Xem logs cả 2 service
docker compose logs -f

# Hoặc xem riêng từng service
docker compose logs -f tei-embedding
docker compose logs -f tei-reranker
```
*(Lần đầu khởi động, hệ thống sẽ tải trọng số mô hình từ Hugging Face về thư mục `./data`, mất khoảng 1-3 phút tùy tốc độ mạng).*

### 4. Tắt hệ thống
```bash
docker compose down
```

---

## 🧪 Kiểm Thử Hệ Thống

Khi các container đã ở trạng thái `healthy`, bạn có thể chạy script kiểm thử tiếng Việt:

### Bằng Python:
```bash
python3 test_tei.py
```

### Bằng Bash cURL:
```bash
./test_tei.sh
```

---

## 🔐 Bảo Mật API Key

Mọi request gọi tới các endpoint suy luận (`/embed`, `/v1/embeddings`, `/rerank`, `/predict`) đều được bảo vệ bởi **API Key**.

Bạn có thể truyền API Key qua 1 trong 2 cách:
- **Header chuẩn Bearer**: `Authorization: Bearer <API_KEY>`
- **Custom Header**: `X-API-Key: <API_KEY>`

API Key mặc định được đặt trong file `.env`:
```env
API_KEY=sk-tei-vietnamese-secret-key
```

---

## 💻 Hướng Dẫn Sử Dụng API

### 1. Lấy Vector Embedding

#### Qua `cURL`:
```bash
curl -X POST http://localhost:8090/embed \
  -H "Authorization: Bearer sk-tei-vietnamese-secret-key" \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": [
      "Hà Nội là thủ đô của Việt Nam.",
      "Trí tuệ nhân tạo đang thay đổi thế giới."
    ],
    "normalize": true
  }'
```

#### Qua Python `requests`:
```python
import requests

response = requests.post(
    "http://localhost:8090/embed",
    headers={
        "Authorization": "Bearer sk-tei-vietnamese-secret-key"
    },
    json={
        "inputs": ["Hà Nội là thủ đô của Việt Nam."],
        "normalize": True
    }
)
embeddings = response.json()
print("Vector length:", len(embeddings[0])) # 1024
```

#### Qua thư viện `openai` Python:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8090/v1",
    api_key="sk-tei-vietnamese-secret-key"
)

response = client.embeddings.create(
    model="BAAI/bge-m3",
    input=["Khám phá ẩm thực truyền thống Việt Nam"]
)
print("Vector:", response.data[0].embedding[:5])
```

---

### 2. Rerank Văn Bản (Đánh giá độ liên quan)

#### Qua `cURL`:
```bash
curl -X POST http://localhost:8090/rerank \
  -H "Authorization: Bearer sk-tei-vietnamese-secret-key" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Thủ đô của Việt Nam là gì?",
    "texts": [
      "Đà Nẵng là thành phố biển miền Trung.",
      "Hà Nội là thủ đô của nước Việt Nam.",
      "TP Hồ Chí Minh là đô thị sầm uất."
    ],
    "return_text": true
  }'
```

#### Kết quả trả về:
```json
[
  {
    "index": 1,
    "score": 0.9984,
    "text": "Hà Nội là thủ đô của nước Việt Nam."
  },
  {
    "index": 2,
    "score": 0.0012,
    "text": "TP Hồ Chí Minh là đô thị sầm uất."
  },
  {
    "index": 0,
    "score": 0.0004,
    "text": "Đà Nẵng là thành phố biển miền Trung."
  }
]
```

---

### 3. Tích hợp LangChain (RAG Pipeline)

```python
from langchain_openai import OpenAIEmbeddings

# Khởi tạo Embeddings với API Key
embeddings = OpenAIEmbeddings(
    base_url="http://localhost:8090/v1",
    api_key="sk-tei-vietnamese-secret-key",
    model="BAAI/bge-m3",
    check_embedding_ctx_length=False
)

# Thử embed query
vec = embeddings.embed_query("Xin chào thế giới")
print(len(vec))
```

---

## ⚙️ Tùy Biến Cấu Hình (`.env`)

Bạn có thể chỉnh sửa file `.env` để thay đổi model hoặc giới hạn tài nguyên:

- **`EMBEDDING_MODEL`**: Mặc định `BAAI/bge-m3`. Nếu muốn model nhẹ hơn cho CPU, có thể đổi thành `intfloat/multilingual-e5-base`.
- **`RERANKER_MODEL`**: Mặc định `BAAI/bge-reranker-v2-m3`. Có thể đổi sang `namdp-ptit/vi-reranker-large` hoặc `BAAI/bge-reranker-base`.
- **`MAX_CLIENT_BATCH_SIZE`**: Số câu tối đa trong 1 request (mặc định: `32`).
- **`MAX_BATCH_TOKENS`**: Số token tối đa TEI gom lại để batching (mặc định: `16384`).
