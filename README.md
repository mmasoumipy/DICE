Sure! Here's a README file for your project:

---

# DICE: Data Interpretation & Computation Engine

DICE (Data Interpretation & Computation Engine) is a **Streamlit-based chat application** that integrates **OpenAI's API** to allow users to upload datasets and ask questions about their data. The application utilizes **OpenAI's Code Interpreter** to analyze and process the uploaded datasets.

## 🚀 Features

- **File Upload**: Users can upload CSV files for analysis.
- **OpenAI Assistant Integration**: Uses OpenAI's assistant to process and interpret data.
- **Code Interpreter**: Executes Python code to analyze datasets.
- **Interactive Chat UI**: Users can interact with the assistant via a chat interface.
- **Content Moderation**: Filters flagged inputs using OpenAI's moderation endpoint.
- **Session Management**: Maintains chat history and uploaded files within the session.

## 🛠️ Installation

### 1. Clone the Repository
```sh
git clone https://github.com/mmasoumipy/DICE.git
cd DICE
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory and add:
```sh
OPENAI_API_KEY=your_openai_api_key
OPENAI_ASSISTANT_ID=your_openai_assistant_id
```

### 4. Run the Application
```sh
streamlit run dice_assistant.py
```

## 📂 Project Structure

```
.
├── dice_assistant.py         # Main Streamlit application
├── requirements.txt    # Required dependencies
├── .env                # API keys (not included in Git)
├── images/             # Folder for storing generated images
└── README.md           # Project documentation
```

## 🏗️ How It Works

1. **Upload CSV File**: The user uploads a dataset.
2. **File Processing**: The dataset is attached to an OpenAI assistant for analysis.
3. **Chat Interaction**: Users input questions about their data.
4. **Code Execution**: The assistant processes queries and returns results.
5. **Display Results**: Outputs include text, images, and code execution logs.

## ⚡ Future Improvements

- Support for multiple file formats (Excel, JSON).
- Improved UI/UX with interactive visualizations.
- Enhanced logging and error handling.

## 🤝 Contributing

Contributions are welcome! Fork the repo, make changes, and submit a PR.