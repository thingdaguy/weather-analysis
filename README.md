# Vietnam Weather Forecast Desktop Application

A modern PyQt6 desktop application with an interactive Leaflet map of Vietnam for weather forecasting.

## Features

- Interactive Leaflet.js map displaying Vietnam
- Click-to-select location functionality
- Real-time coordinate display (latitude, longitude)
- Red marker placement on map
- Python-JavaScript communication via QWebChannel
- Modern, clean UI design
- Responsive and fast performance

## Project Objectives

- Automate data collection from external APIs
- Centralize data processing and storage
- Train and evaluate machine learning models
- Support scalable client–server architecture

---

## Key Features

- 🔄 Automated data fetching (Client-side)
- 🧹 Data cleaning & preprocessing
- 🧠 Machine Learning model training
- 📈 Model evaluation & validation
- 💾 Model persistence for reuse


## System Architecture

Client ↔ REST API ↔ Server ↔ ML Engine ↔ Data Storage



## 📂 Project Structure

```
Python/
├── Client/                 # Client-side data acquisition
│   ├── fetchApi/           # API fetching & data retrieval
│   └── __pycache__/        # Python cache files
├── server/                 # Backend & Machine Learning core
│   ├── data/
│   │   ├── raw/            # Raw, unprocessed data
│   │   └── processed/      # Cleaned & feature-engineered data
│   ├── models/             # Trained ML models
│   └── test_model.ipynb    # Model testing & validation notebook
└── README.md               # Project documentation
```
---
🛠 Installation & Setup
# Prerequisites

```

  🐍 Python 3.8+ 

  🔧 Git

  📒 Jupyter Notebook (optional)

````
---
## Step 1: Clone the Repository

python -m venv venv

## Windows
.\venv\Scripts\activate

## macOS / Linux

source venv/bin/activate

---

## Step 2: Environment Setup

python -m venv venv

## Windows

.\venv\Scripts\activate

## macOS / Linux

source venv/bin/activate

---

## Step 3: Install Dependencies

pip install -r requirements.txt

---

## Step 4: Run the System
```
Start Server (Backend & ML Engine)
cd server
python ml_api.py
```

---

```
Start Client (Data Acquisition)
cd Client
python main.py
```
---
## ⚙️ System Workflow

      Data Collection
      
      Client fetches data from external APIs.
      
      Raw data is sent to the Server.
      
      Raw data is stored in server/data/raw/.
      
      Data Preprocessing
      
      Cleaning, normalization, and feature engineering.
      
      Processed data is saved in server/data/processed/.
      
      Model Training
      
      Models are trained using processed data.
      
      Trained models are saved for reuse.
      
      Model Evaluation
      
      Performance is evaluated using metrics such as accuracy and loss.

## 🧠 Machine Learning
## Supported tasks:
```
   Classification

   Regression

   Predictive analytics

   Model files are stored in :

      server/models/

```

## Purpose & Key Features
```
⭐ Purpose (Tác dụng của dự án)
  ```
      This project provides a complete end-to-end machine learning pipeline, helping users to:
    
      Automate data collection, processing, and analysis
    
      Reduce manual effort in data handling and model training
    
      Standardize ML workflows for learning and experimentation
    
      Serve as a foundation for data-driven applications
    
      Support academic projects, research, and real-world ML experiments

  ```
⭐ Key Features (Tính năng chính)
  ```
    🔹 Client-side
    ```
    Automated data collection from external APIs

    Configurable data sources and parameters

    Lightweight client module

    REST API communication

    ```
    🔹 Server-side
    ```
    Centralized storage for raw & processed data

    Data preprocessing:

    Cleaning

    Normalization

    Feature engineering

    Machine learning model training & evaluation

    Model persistence for reproducibility

    ```
    🔹 Experimentation & Testing
    ```
    Jupyter Notebook support

    Model testing and validation

    Performance visualization

    Hyperparameter tuning
    ```
  ```
```

## 🧩 Project Value & Practical Benefits

 #### 🔍 Overall Impact
  ```
    The Data Analysis & Model Pipeline bridges the gap between raw data collection and machine learning intelligence.

    It enables users to build scalable, reusable, and maintainable data systems and is suitable for:

    Students learning Data Science & Machine Learning

    Developers practicing Client–Server architecture

    Researchers experimenting with ML models

    ML-ready backend system prototyping

  ```
####  🏗 Architectural Advantages
  ```
    Client–Server separation

    Modular and extensible design

    Scalable data pipeline

    Clear folder structure and maintainability

  ```
#### 📊 Technologies Used
  ```
    🐍 Python

    📦 Pandas / NumPy

    🤖 Scikit-learn / TensorFlow / PyTorch

    📒 Jupyter Notebook

    🌐 REST API

    🔧 Git
  ```
#### Future Improvements
  ```
    Swagger / OpenAPI documentation

    Docker-based deployment

    Scheduled data pipelines

    Logging and monitoring

    CI/CD integration
  ```
 #### 🤝 Contribution
```
    Contributions are welcome:

    Fork the repository

    Create a new branch

    Commit your changes

    Open a Pull Request
```
#### 📄 License
  ```
    This project is licensed under the MIT License.

    You are free to use, modify, and distribute this project with attribution.
    
  ```

# Ứng Dụng Dự Báo Thời Tiết Việt Nam Trên Desktop

Một ứng dụng desktop hiện đại sử dụng PyQt6 với bản đồ tương tác Leaflet của Việt Nam dành cho dự báo thời tiết.

## Tính Năng

- Bản đồ tương tác Leaflet.js hiển thị Việt Nam
- Chức năng chọn vị trí bằng cách click
- Hiển thị tọa độ thời gian thực (vĩ độ, kinh độ)
- Đặt marker đỏ trên bản đồ
- Giao tiếp Python-JavaScript qua QWebChannel
- Thiết kế UI hiện đại, sạch sẽ
- Hiệu suất responsive và nhanh chóng

## Mục Tiêu Dự Án

- Tự động hóa thu thập dữ liệu từ các API bên ngoài
- Tập trung hóa xử lý và lưu trữ dữ liệu
- Huấn luyện và đánh giá các mô hình machine learning
- Hỗ trợ kiến trúc client-server có khả năng mở rộng

## Tính Năng Chính

- 🔄 Tự động lấy dữ liệu (Phía Client)
- 🧹 Làm sạch & tiền xử lý dữ liệu
- 🧠 Huấn luyện mô hình Machine Learning
- 📈 Đánh giá & xác thực mô hình
- 💾 Lưu trữ mô hình để tái sử dụng

## Kiến Trúc Hệ Thống

Client ↔ REST API ↔ Server ↔ ML Engine ↔ Data Storage

text

## Cấu Trúc Dự Án

Python/
├── Client/ # Thu thập dữ liệu phía client
│ ├── fetchApi/ # Lấy dữ liệu từ API
│ └── pycache/ # File cache Python
├── server/ # Lõi backend & Machine Learning
│ ├── data/
│ │ ├── raw/ # Dữ liệu thô, chưa xử lý
│ │ └── processed/ # Dữ liệu đã làm sạch & kỹ thuật đặc trưng
│ ├── models/ # Các mô hình ML đã huấn luyện
│ └── test_model.ipynb # Notebook kiểm tra & xác thực mô hình
└── README.md # Tài liệu dự án

text

## Cài Đặt & Thiết Lập

### Yêu Cầu Tiên Quyết

- 🐍 Python 3.8+
- 🔧 Git
- 📒 Jupyter Notebook (tùy chọn)

### Bước 1: Clone Repository

git clone [URL repository] # Thay bằng URL thực tế
cd [tên thư mục dự án]

text

### Bước 2: Thiết Lập Môi Trường Ảo

python -m venv venv

text

**Windows:**
.\venv\Scripts\activate

text

**macOS / Linux:**
source venv/bin/activate

text

### Bước 3: Cài Đặt Các Thư Viện

pip install -r requirements.txt

text

### Bước 4: Chạy Hệ Thống

**Khởi Động Server (Backend & ML Engine):**
cd server
python ml_api.py

text

**Khởi Động Client (Thu Thập Dữ Liệu):**
cd Client
python main.py

text

## Quy Trình Hoạt Động Hệ Thống

### Thu Thập Dữ Liệu

1. Client lấy dữ liệu từ các API bên ngoài
2. Dữ liệu thô được gửi đến Server
3. Dữ liệu thô được lưu trong `server/data/raw/`

### Tiền Xử Lý Dữ Liệu

1. Làm sạch, chuẩn hóa và kỹ thuật đặc trưng
2. Dữ liệu đã xử lý được lưu trong `server/data/processed/`

### Huấn Luyện Mô Hình

1. Huấn luyện mô hình sử dụng dữ liệu đã xử lý
2. Các mô hình đã huấn luyện được lưu để tái sử dụng

### Đánh Giá Mô Hình

- Đánh giá hiệu suất bằng các chỉ số như độ chính xác và loss

## Machine Learning

### Các Nhiệm Vụ Hỗ Trợ

- Phân loại (Classification)
- Hồi quy (Regression)
- Phân tích dự đoán (Predictive analytics)

**Lưu trữ mô hình:** `server/models/`

## Mục Đích & Tính Năng Chính

### Mục Đích Dự Án

Dự án này cung cấp một pipeline machine learning end-to-end hoàn chỉnh, giúp người dùng:

- Tự động hóa thu thập, xử lý và phân tích dữ liệu
- Giảm nỗ lực thủ công trong xử lý dữ liệu và huấn luyện mô hình
- Chuẩn hóa quy trình ML để học tập và thử nghiệm
- Làm nền tảng cho các ứng dụng dựa trên dữ liệu
- Hỗ trợ dự án học thuật, nghiên cứu và thí nghiệm ML thực tế

### Phía Client

- Tự động thu thập dữ liệu từ các API bên ngoài
- Cấu hình nguồn dữ liệu và tham số linh hoạt
- Module client nhẹ
- Giao tiếp REST API

### Phía Server

- Lưu trữ tập trung cho dữ liệu thô & đã xử lý
- Tiền xử lý dữ liệu: Làm sạch, Chuẩn hóa, Kỹ thuật đặc trưng
- Huấn luyện & đánh giá mô hình machine learning
- Lưu trữ mô hình để tái lập

### Thử Nghiệm & Kiểm Tra

- Hỗ trợ Jupyter Notebook
- Kiểm tra và xác thực mô hình
- Trực quan hóa hiệu suất
- Tinh chỉnh siêu tham số

## Giá Trị Dự Án & Lợi Ích Thực Tế

### Tác Động Tổng Thể

Pipeline Phân Tích Dữ Liệu & Mô Hình bắc cầu khoảng cách giữa thu thập dữ liệu thô và trí tuệ machine learning. Nó cho phép người dùng xây dựng hệ thống dữ liệu có khả năng mở rộng, tái sử dụng và dễ bảo trì, phù hợp cho:

- Sinh viên học Data Science & Machine Learning
- Lập trình viên thực hành kiến trúc Client–Server
- Nhà nghiên cứu thử nghiệm mô hình ML
- Nguyên mẫu hệ thống backend sẵn sàng cho ML

### Ưu Điểm Kiến Trúc

- Tách biệt Client–Server
- Thiết kế modular và dễ mở rộng
- Pipeline dữ liệu có khả năng mở rộng
- Cấu trúc thư mục rõ ràng và dễ bảo trì

## Công Nghệ Sử Dụng

- 🐍 Python
- 📦 Pandas / NumPy
- 🤖 Scikit-learn / TensorFlow / PyTorch
- 📒 Jupyter Notebook
- 🌐 REST API
- 🔧 Git

## Cải Tiến Tương Lai

- Tài liệu Swagger / OpenAPI
- Triển khai dựa trên Docker
- Pipeline dữ liệu theo lịch trình
- Logging và monitoring
- Tích hợp CI/CD

## Đóng Góp

Các đóng góp được hoan nghênh:

1. Fork repository
2. Tạo branch mới
3. Commit thay đổi
4. Mở Pull Request

## Giấy Phép

Dự án này được cấp phép theo MIT License.
Bạn tự do sử dụng, sửa đổi và phân phối dự án với ghi công.


