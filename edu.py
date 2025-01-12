from langchain_google_genai import ChatGoogleGenerativeAI
# Updated import to fix deprecation warning
from langchain_community.vectorstores import Chroma
from educhain import Educhain, LLMConfig
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urlparse
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuizGenerator:
    """Quiz generator using Educhain with Gemini model integration."""
    
    def __init__(self, api_key: str):
        """
        Initialize the quiz generator with Gemini model.
        
        Args:
            api_key: Google API key for Gemini
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        # Initialize Gemini model with retry mechanism
        try:
            gemini_model = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro",
                google_api_key=api_key,
                temperature=0.7,  # Add some variety to questions
                max_output_tokens=2048  # Ensure enough tokens for detailed responses
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Gemini model: {str(e)}")
            
        # Configure Educhain with Gemini
        model_config = LLMConfig(custom_model=gemini_model)
        self.client = Educhain(model_config)
        
        # Create output directory
        self.output_dir = "quizzes"
        os.makedirs(self.output_dir, exist_ok=True)
    
    # Rest of the class methods remain the same...
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_topic_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        question_type: str = "Multiple Choice",
        difficulty: str = "Medium"
    ) -> Dict:
        """
        Generate quiz questions for a given topic with retry mechanism.
        
        Args:
            topic: Subject topic
            num_questions: Number of questions to generate
            question_type: Type of questions (Multiple Choice, True/False, Open-ended)
            difficulty: Difficulty level (Easy, Medium, Hard)
        
        Returns:
            Dictionary containing generated questions or error message
        """
        # Validate inputs
        if not topic or not isinstance(topic, str):
            raise ValueError("Topic must be a non-empty string")
        if not isinstance(num_questions, int) or num_questions < 1:
            raise ValueError("Number of questions must be a positive integer")
        if difficulty not in ["Easy", "Medium", "Hard"]:
            raise ValueError("Difficulty must be Easy, Medium, or Hard")
            
        template = f"""
        Generate {num_questions} {question_type} questions about {topic}.
        Difficulty: {difficulty}
        
        Requirements:
        - Questions must be clear, concise, and unambiguous
        - Cover different aspects of {topic}
        - Match {difficulty} difficulty level
        - Include detailed explanations for correct answers
        - Each question must have exactly one correct answer
        - For Multiple Choice, provide exactly 4 options
        
        Output format:
        - Each question object must have: question, options, answer, explanation
        - Answer should be the letter (A, B, C, D) for Multiple Choice
        """
        
        try:
            questions = self.client.qna_engine.generate_questions(
                topic=topic,
                num=num_questions,
                question_type=question_type,
                prompt_template=template
            )
            
            # Validate generated questions
            quiz_data = questions.dict()
            self._validate_quiz_data(quiz_data)
            return quiz_data
            
        except Exception as e:
            logger.error(f"Failed to generate topic quiz: {str(e)}")
            return {
                "error": f"Failed to generate topic quiz: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "params": {
                    "topic": topic,
                    "num_questions": num_questions,
                    "type": question_type,
                    "difficulty": difficulty
                }
            }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_url_quiz(
        self,
        url: str,
        num_questions: int = 5,
        question_type: str = "Multiple Choice"
    ) -> Dict:
        """
        Generate quiz questions from a URL with retry mechanism.
        
        Args:
            url: Source URL
            num_questions: Number of questions
            question_type: Type of questions
        
        Returns:
            Dictionary containing generated questions or error message
        """
        # Validate URL
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Invalid URL provided")

        try:
            questions = self.client.qna_engine.generate_questions_from_data(
                source=url,
                source_type="url",
                num=num_questions,
                question_type=question_type
            )
            
            # Validate generated questions
            quiz_data = questions.dict()
            self._validate_quiz_data(quiz_data)
            return quiz_data
            
        except Exception as e:
            logger.error(f"Failed to generate URL quiz: {str(e)}")
            return {
                "error": f"Failed to generate URL quiz: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "params": {
                    "url": url,
                    "num_questions": num_questions,
                    "type": question_type
                }
            }

    def _validate_quiz_data(self, quiz_data: Dict) -> None:
        """
        Validate the structure and content of generated quiz data.
        
        Args:
            quiz_data: Dictionary containing quiz questions
            
        Raises:
            ValueError: If quiz data is invalid
        """
        if not isinstance(quiz_data, dict):
            raise ValueError("Quiz data must be a dictionary")
            
        if "questions" not in quiz_data:
            raise ValueError("Quiz data must contain 'questions' key")
            
        for i, question in enumerate(quiz_data["questions"]):
            required_keys = {"question", "options", "answer", "explanation"}
            if not all(key in question for key in required_keys):
                raise ValueError(f"Question {i+1} missing required fields: {required_keys}")
                
            if not isinstance(question["options"], list):
                raise ValueError(f"Options for question {i+1} must be a list")
                
            if len(question["options"]) != 4:
                raise ValueError(f"Question {i+1} must have exactly 4 options")

    def save_quiz(self, quiz_data: Dict, quiz_type: str) -> str:
        """
        Save generated quiz to a JSON file with error handling.
        
        Args:
            quiz_data: Quiz content
            quiz_type: Type of quiz (topic/url)
        
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quiz_{quiz_type}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(quiz_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved quiz to {filepath}")
            return filepath
        except Exception as e:
            error_msg = f"Failed to save quiz: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg)

def main():
    """Main function with error handling and logging."""
    try:
        # Directly use the API key instead of environment variable
        GOOGLE_API_KEY = 'AIzaSyD8FbT54AoI1BZzMKErr-0tM6xGNDFVQVk'  # Your API key
        
        generator = QuizGenerator(GOOGLE_API_KEY)
        
        # Generate topic-based quiz
        logger.info("Generating topic-based quiz...")
        topic_quiz = generator.generate_topic_quiz(
            topic="Artificial Intelligence",
            num_questions=3,
            question_type="Multiple Choice",
            difficulty="Medium"
        )
        topic_file = generator.save_quiz(topic_quiz, "topic")
        logger.info(f"Topic quiz saved to: {topic_file}")
        
        # Generate URL-based quiz
        logger.info("Generating URL-based quiz...")
        url_quiz = generator.generate_url_quiz(
            url="https://en.wikipedia.org/wiki/Artificial_intelligence",
            num_questions=3
        )
        url_file = generator.save_quiz(url_quiz, "url")
        logger.info(f"URL quiz saved to: {url_file}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()