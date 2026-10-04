# 📐 AI Vision Math & Homework Tutor

An interactive web application powered by **Streamlit** and **Google Gemini AI** designed to serve as a Socratic math and science tutor. Instead of simply giving away answers, the tutor transcribes handwritten equations into formatted LaTeX, identifies errors in student work, and provides helpful hints to guide them toward the correct solution.

---

## ✨ Features

- **📷 Image & PDF Processing**: Upload images (`.png`, `.jpg`, `.jpeg`, `.webp`, `.jfif`) or multi-page `.pdf` documents containing handwritten problems.
- **✂️ Non-Blocking Equation Cropping**: Crop images directly inside the app to focus the AI on a specific equation or step without UI lag.
- **⚡ High-Performance Streaming**: Real-time response streaming for instant feedback.
- **🔁 Resilient Fallback Loop**: Automatically retries using secondary models (`gemini-3.5-flash-lite`, `gemini-3.7-flash`, `gemini-3.8-flash`) if primary API endpoints experience temporary unavailability (`503` errors).
- **💬 Socratic Multi-Turn Chat**: Follow up with questions or ask for additional hints while retaining image context.
- **📥 Session Summary Export**: Download your entire problem-solving history as a structured `.md` (Markdown) file for study revision.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **AI Model Client**: Google GenAI SDK (`google-genai`)
- **Image & PDF Manipulation**: `Pillow`, `streamlit-cropper`, `pypdf`
- **Deployment Platform**: Render / Streamlit Community Cloud

---

## 🚀 Local Setup Instructions

### Prerequisites
- Python 3.10+ (Tested up to Python 3.14)
- A valid **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/math-tutor.git
cd math-tutor
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.streamlit/secrets.toml` file in the root directory:
```toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

> **Warning:** Never commit `.streamlit/secrets.toml` to Git! Make sure it is listed in your `.gitignore` file.

### 5. Run the Application
```bash
streamlit run app.py
```

---

## ☁️ Environment Variables (Deployment)

When deploying to platforms like Render, set the following environment variable in your dashboard:

| Variable Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key |

---

## 📄 License

This project is open-source under the MIT License.