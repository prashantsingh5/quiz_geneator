# Quiz Generator Using LangChain and Educhain 🧠📚

This project is a Python-based quiz generation tool that uses LangChain, Educhain, and the Gemini 1.5 Pro model to create educational quizzes. It can generate quizzes based on topics or URLs and save the output as structured JSON files. The application includes features like retry mechanisms, detailed logging, and robust input validation.

---

## Features 🚀
- **Topic-based Quiz Generation**: Generates quizzes for a given topic with configurable parameters such as the number of questions, question type, and difficulty level.
- **URL-based Quiz Generation**: Creates quizzes from web content by providing a source URL.
- **Gemini Model Integration**: Utilizes Google Generative AI for high-quality question generation.
- **Customizable Parameters**: Configure quiz types, question count, and difficulty to suit your needs.
- **Retry Mechanism**: Ensures stability with automatic retries for transient errors.
- **Output Validation**: Validates generated quizzes to ensure structural integrity.
- **Error Handling**: Logs errors with detailed messages for debugging.
- **Output Directory**: Saves quizzes as JSON files in a designated `quizzes` folder.

---

## Tech Stack 🛠️
- **Python**: Core programming language.
- **LangChain**: For integration with language models and question generation.
- **Educhain**: Provides an abstraction layer for quiz generation.
- **Gemini 1.5 Pro**: Google Generative AI for natural language processing.
- **Logging**: For runtime error tracking and debugging.
- **Tenacity**: Implements retry mechanisms for API calls.

---

## Installation 🛠️

### Clone the repository:
```bash
git clone https://github.com/your-repo-name/quiz-generator.git
cd quiz-generator
```

## Install dependencies:
```bash 
pip install -r requirements.txt
```

## Set up API credentials:
Create a .env file in the project directory:
```bash
  GOOGLE_API_KEY=your_google_api_key
```

## How to Use 🏃‍♂️
### 1. Topic-based Quiz Generation
Generates quizzes based on a specified topic.
```bash
generator.generate_topic_quiz(
    topic="Artificial Intelligence",
    num_questions=5,
    question_type="Multiple Choice",
    difficulty="Medium"
)
```

### 2. URL-based Quiz Generation
Extracts content from a URL and generates quiz questions.
```bash
generator.generate_url_quiz(
    url="https://en.wikipedia.org/wiki/Artificial_intelligence",
    num_questions=5,
    question_type="Multiple Choice"
)
```
### 3. Saving Quizzes
All generated quizzes are saved in the quizzes folder with filenames like quiz_topic_YYYYMMDD_HHMMSS.json.
```bash
generator.save_quiz(quiz_data, quiz_type="topic")
```

## File Structure 📂
```bash
quiz-generator/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── quizzes/               # Directory for saved quizzes
│   ├── quiz_topic_<timestamp>.json
│   └── quiz_url_<timestamp>.json
├── README.md              # Project documentation
└── .env                   # Environment variables for API credentials
```

## Example Outputs 📑
### 1. Topic-based Quiz (Example)
File: quizzes/quiz_topic_<timestamp>.json
```bash
{
  "questions": [
    {
      "question": "Which of the following is NOT a common technique used in Natural Language Processing (NLP)?",
      "options": ["A. Tokenization", "B. Backpropagation", "C. Named Entity Recognition", "D. Sentiment Analysis"],
      "answer": "B",
      "explanation": "While backpropagation is crucial for neural networks, it is not a direct NLP technique."
    }
  ]
}
```

## Future Enhancements 🔮
- Advanced Retry Logic: Improve handling for rate-limiting errors.
- Cloud Deployment: Deploy the application as a web service.
- Multi-language Support: Enable quiz generation in multiple languages.
- Enhanced Validation: Add richer checks for quiz data integrity.

