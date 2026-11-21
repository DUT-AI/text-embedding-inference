# 📖 Tài Liệu Hướng Dẫn Sử Dụng Dịch Vụ Text Embeddings & Reranking (DUT AI)

- **Domain chính thức**: `https://textembedding.dutai.io.vn`
- **Dịch vụ**: Hugging Face Text Embeddings Inference (TEI) tối ưu cho tiếng Việt
- **Mô hình phục vụ**:
  - 🧠 **Embedding**: `BAAI/bge-m3` (1024 dimensions, context 8192 tokens)
  - 🎯 **Reranking**: `BAAI/bge-reranker-v2-m3` (Cross-encoder, context 8192 tokens)

---

## 🔐 1. Xác Thực (Authentication)

Tất cả các endpoint suy luận đều yêu cầu API Key. Bạn có thể truyền qua 1 trong 2 cách:

1. **Header chuẩn Bearer Token**:
   ```http
   Authorization: Bearer <YOUR_API_KEY>
   ```
2. **Custom Header**:
   ```http
   X-API-Key: <YOUR_API_KEY>
   ```

> [!NOTE]
> Thay `<YOUR_API_KEY>` bằng API Key mà bạn đã thiết lập (ví dụ: `dutaiclb`).

---

## 🌐 2. Bảng Tổng Hợp Endpoints

| Tác vụ | Endpoint URL | Method | Mô tả |
| :--- | :--- | :--- | :--- |
| **System Info** | `https://textembedding.dutai.io.vn/` | `GET` | Kiểm tra thông tin & trạng thái dịch vụ (Public) |
| **Health Check** | `https://textembedding.dutai.io.vn/health/embedding`<br>`https://textembedding.dutai.io.vn/health/rerank` | `GET` | Kiểm tra tình trạng hoạt động của từng model |
| **Embedding (TEI Native)** | `https://textembedding.dutai.io.vn/embed` | `POST` | Trả về trực tiếp mảng vector embedding |
| **Embedding (OpenAI format)** | `https://textembedding.dutai.io.vn/v1/embeddings` | `POST` | Tương thích 100% với chuẩn OpenAI SDK / LangChain |
| **Reranking** | `https://textembedding.dutai.io.vn/rerank` | `POST` | Đánh giá và sắp xếp độ liên quan văn bản |

---

## 📘 3. Hướng Dẫn Sử Dụng API Embedding

Tạo vector embedding cho một hoặc nhiều câu/đoạn văn bản tiếng Việt.

### 3.1. Endpoint Chuẩn TEI (`/embed`)

- **URL**: `https://textembedding.dutai.io.vn/embed`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "inputs": [
      "Hà Nội là thủ đô của Việt Nam.",
      "Trí tuệ nhân tạo đang phát triển vượt bậc."
    ],
    "normalize": true,
    "truncate": true
  }
  ```

#### Code mẫu cURL:
```bash
curl -X POST https://textembedding.dutai.io.vn/embed \
  -H "Authorization: Bearer dutaiclb" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": ["Hà Nội là thủ đô của Việt Nam."],
    "normalize": true
  }'
```

#### Code mẫu Python (`requests`):
```python
import requests

url = "https://textembedding.dutai.io.vn/embed"
headers = {
    "Authorization": "Bearer dutaiclb",
    "Content-Type": "application/json"
}
payload = {
    "inputs": [
        "Hà Nội là thủ đô của Việt Nam.",
        "Đà Nẵng là thành phố đáng sống."
    ],
    "normalize": True
}

response = requests.post(url, headers=headers, json=payload)
embeddings = response.json()

print(f"Số lượng vector: {len(embeddings)}")
print(f"Kích thước vector: {len(embeddings[0])} dimensions")
```

---

### 3.2. Endpoint Tương thích OpenAI (`/v1/embeddings`)

Dùng trực tiếp với thư viện OpenAI SDK chính thức của Python / NodeJS / Go / v.v.

#### Python OpenAI SDK:
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://textembedding.dutai.io.vn/v1",
    api_key="dutaiclb"
)

response = client.embeddings.create(
    model="BAAI/bge-m3",
    input=[
        "Khoa học máy tính và hệ thống nhúng",
        "Mô hình ngôn ngữ lớn và tìm kiếm ngữ nghĩa"
    ]
)

for item in response.data:
    print(f"Index {item.index}: Vector length = {len(item.embedding)}")
```

---

## 📗 4. Hướng Dẫn Sử Dụng API Reranking

Reranker đóng vai trò tính điểm tương đồng chéo (Cross-Encoder) giữa `query` của người dùng và danh sách các đoạn văn bản trích xuất từ database (Retrieval) để chọn ra các đoạn văn bản liên quan nhất.

- **URL**: `https://textembedding.dutai.io.vn/rerank`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "query": "Thủ đô của Việt Nam là gì?",
    "texts": [
      "Đà Nẵng có nhiều bãi biển đẹp và cây cầu Rồng nổi tiếng.",
      "Hà Nội là thủ đô của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam.",
      "Thành phố Hồ Chí Minh là trung tâm tài chính lớn nhất miền Nam."
    ],
    "return_text": true,
    "truncate": true
  }
  ```

#### Code mẫu cURL:
```bash
curl -X POST https://textembedding.dutai.io.vn/rerank \
  -H "Authorization: Bearer dutaiclb" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Thủ đô của Việt Nam là gì?",
    "texts": [
      "Đà Nẵng có bãi biển đẹp.",
      "Hà Nội là thủ đô của Việt Nam.",
      "TP Hồ Chí Minh rất sôi động."
    ],
    "return_text": true
  }'
```

#### Response mẫu:
```json
[
  {
    "index": 1,
    "score": 0.9982,
    "text": "Hà Nội là thủ đô của Việt Nam."
  },
  {
    "index": 2,
    "score": 0.0014,
    "text": "TP Hồ Chí Minh rất sôi động."
  },
  {
    "index": 0,
    "score": 0.0004,
    "text": "Đà Nẵng có bãi biển đẹp."
  }
]
```

#### Code mẫu Python (`requests`):
```python
import requests

url = "https://textembedding.dutai.io.vn/rerank"
headers = {
    "Authorization": "Bearer dutaiclb",
    "Content-Type": "application/json"
}
payload = {
    "query": "Học bổng sinh viên xuất sắc cần điều kiện gì?",
    "texts": [
      "Thời khóa biểu học kỳ 1 năm học 2026.",
      "Quy định xét cấp học bổng khuyến khích học tập yêu cầu điểm rèn luyện từ 80 trở lên và GPA loại Giỏi.",
      "Lịch thi tốt nghiệp THPT quốc gia."
    ],
    "return_text": True
}

response = requests.post(url, headers=headers, json=payload)
results = response.json()

print("--- KẾT QUẢ RERANK ---")
for rank, item in enumerate(results, 1):
    print(f"Top {rank} (Score: {item['score']:.4f}): {item['text']}")
```

---

## 🤖 5. Tích Hợp Vào Các Framework RAG Phổ Biến

### 5.1. LangChain (Python)

```python
from langchain_openai import OpenAIEmbeddings

# 1. Khởi tạo Embeddings
embeddings = OpenAIEmbeddings(
    base_url="https://textembedding.dutai.io.vn/v1",
    api_key="dutaiclb",
    model="BAAI/bge-m3",
    check_embedding_ctx_length=False
)

# 2. Embed câu truy vấn
query_vector = embeddings.embed_query("Trường Đại học Bách Khoa")
print("Độ dài vector:", len(query_vector))

# 3. Embed danh sách văn bản
doc_vectors = embeddings.embed_documents([
    "Khoa Công nghệ Thông tin",
    "Viện Nghiên cứu Trí tuệ Nhân tạo"
])
```

---

### 5.2. LlamaIndex (Python)

```python
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(
    api_base="https://textembedding.dutai.io.vn/v1",
    api_key="dutaiclb",
    model_name="BAAI/bge-m3"
)

vector = embed_model.get_text_embedding("Hệ thống thông tin quản lý")
print("Vector length:", len(vector))
```

---

### 5.3. NodeJS / TypeScript (`axios` hoặc `fetch`)

```typescript
import axios from "axios";

const API_BASE = "https://textembedding.dutai.io.vn";
const API_KEY = "dutaiclb";

// 1. Tạo Embeddings
async function getEmbedding(text: string) {
  const response = await axios.post(
    `${API_BASE}/embed`,
    {
      inputs: [text],
      normalize: true
    },
    {
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json"
      }
    }
  );
  return response.data[0];
}

// 2. Rerank văn bản
async function rerank(query: string, docs: string[]) {
  const response = await axios.post(
    `${API_BASE}/rerank`,
    {
      query: query,
      texts: docs,
      return_text: true
    },
    {
      headers: {
        Authorization: `Bearer ${API_KEY}`,
        "Content-Type": "application/json"
      }
    }
  );
  return response.data;
}
```

---

### 5.4. Tích Hợp Vào Dify / FastGPT / AnythingLLM / Flowise

Khi cấu hình Model Provider trong các nền tảng AI Agent / RAG:

| Trường Cấu Hình | Giá Trị Điền |
| :--- | :--- |
| **Provider Type** | `OpenAI-API-compatible` |
| **Model Type** | `Text Embedding` |
| **Model Name** | `BAAI/bge-m3` |
| **Server URL / Base URL** | `https://textembedding.dutai.io.vn/v1` |
| **API Key** | `dutaiclb` |
| **Max Tokens** | `8192` |
| **Dimensions** | `1024` |

---

## ⚠️ 6. Bảng Mã Lỗi (Error Codes)

| HTTP Code | Ý nghĩa | Cách khắc phục |
| :--- | :--- | :--- |
| **`200 OK`** | Thành công | Request hợp lệ. |
| **`401 Unauthorized`** | Thiếu hoặc sai API Key | Kiểm tra lại header `Authorization: Bearer <API_KEY>` hoặc `X-API-Key`. |
| **`422 Unprocessable Entity`** | Payload sai định dạng | Kiểm tra cấu trúc JSON (ví dụ: `inputs` phải là list các chuỗi hoặc chuỗi). |
| **`413 Payload Too Large`** | Vượt quá giới hạn kích thước | Giảm số lượng câu trong một lần gửi (batch size khuyến nghị $\le 32$). |
| **`502 / 504 Gateway Error`** | Service đang bận hoặc quá tải | Giảm `max_batch_tokens` hoặc thử lại sau vài giây. |

---

## 📞 Hỗ Trợ Kỹ Thuật
Nếu gặp bất kỳ vấn đề nào trong quá trình tích hợp, vui lòng liên hệ quản trị viên hệ thống DUT AI.
