# 🧠 Personalized Learning Assistant

### *An interactive learning experience that adapts to your unique knowledge level.*

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Gradio](https://img.shields.io/badge/Gradio-4.31-orange?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-lightgrey?style=for-the-badge)
![Kaggle](https://img.shields.io/badge/Kaggle-Gemma%203n%20Challenge-blue?style=for-the-badge&logo=kaggle)

This project is a submission for the **[Google - The Gemma 3n Impact Challenge](https://www.kaggle.com/competitions/google-gemma-3n-hackathon)** on Kaggle. Its purpose is to demonstrate how next-generation local AI models can revolutionize education.

---

## 📖 About The Project

The Personalized Learning Assistant is a revolutionary learning tool, powered by Google's state-of-the-art **Gemma 3n** model, designed to overcome one of the biggest obstacles in education: the "one-size-fits-all" approach. This intelligent assistant smartly assesses each user's current knowledge level on a topic and then creates a dynamic, completely personalized learning path with custom-generated content, reinforcement quizzes, and interactive Q&A sessions. By running this entire process locally on the user's device, our project makes learning not only more effective but also **completely private and accessible offline.**

![Application Interface](https://i.imgur.com/link-to-your-main-screenshot.png) 
*(NOTE: Replace this link with a link to a main screenshot of your application.)*

---

## 🚀 Key Features

* **🎓 Adaptive Level Assessment:** Dynamically generates an initial quiz to determine the user's knowledge level (Beginner, Intermediate, Advanced).
* **✍️ Personalized Content:** Creates tailored topic explanations and suggests resources from scratch, based on the assessed level.
* **🧩 Knowledge Reinforcement:** Offers a 10-question mini-quiz to solidify learning and ensure retention.
* **💡 Interactive Feedback:** Provides detailed explanations for incorrect quiz answers, not just showing the right answer but explaining the *why* behind it for true comprehension.
* **💭 Deep Dive Q&A:** Allows users to ask any follow-up questions about the generated content, enabling curiosity and a deeper exploration of the topic.
* **🌐 Bilingual Support:** Fully functional in both English and Turkish.
* **🔒 100% Private & Offline:** Powered by `Ollama`, all processing happens on the user's own device. No data ever leaves the machine, and no internet connection is required.

---

## ✨ The Core Idea: The Adaptive Learning Loop

Our project guides the user through a pedagogically sound, four-step learning cycle to maximize learning outcomes:

1.  **ASSESS:** What do you know? The app first measures your current proficiency with a short pre-quiz.
2.  **LEARN:** Fill in your knowledge gaps by reading content that is custom-generated for your specific level.
3.  **TEST:** Solidify your new knowledge by taking a mini-quiz that tests for comprehension.
4.  **DEEPEN:** Achieve mastery by asking specific questions in the interactive Q&A section to clarify any points of confusion or curiosity.

---

## 💡 Why Gemma 3n? The Power of Local AI

The choice of the **Gemma 3n** model for this project was a deliberate, strategic decision. Our goal was to leverage the model's unique capabilities to solve real-world problems.

* **Privacy & Trust:** Gemma 3n's ability to run locally ensures complete privacy in a sensitive domain like education. Users' learning data and personal information never leave their own devices.
* **Accessibility:** By functioning without an internet connection, the application bridges the digital divide, making quality learning tools accessible to people in any geographic or socio-economic situation.
* **Versatility:** In this project, we used Gemma 3n not as a simple chatbot, but as a multi-faceted **Assessment Designer**, a **Personalized Tutor**, a **Quiz Master**, and a **Socratic Q&A Partner**. This showcases the model's flexibility and its potential in a wide range of complex tasks.

---

## 🛠️ Setup and Installation

### Prerequisites
Before you begin, ensure you have the following installed on your system:

1.  **Python 3.8+**
2.  **Ollama:** Download and install it from [ollama.com](https://ollama.com/).
3.  **The gemma3n Model:** Pull the model by running the following command in your terminal:
    ```bash
    ollama pull gemma3n:latest
    ```

### Installation Steps

1.  Clone this repository to your local machine:
    ```bash
    git clone [https://github.com/Harungokc/Personalized-Learning-Assistant.git](https://github.com/Harungokc/Personalized-Learning-Assistant.git)
    cd personalized-learning-assistant
    ```
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  Ensure the Ollama application is running in the background.
2.  Run the application from your terminal:
    ```bash
    python app.py
    ```
3.  Open the local URL provided in the terminal (usually `http://127.0.0.1:7860`) in your web browser.

---

## 💻 Technologies Used

* **Python:** The core programming language.
* **Gradio:** For the interactive web UI.
* **Ollama:** For running the AI model locally.
* **Gemma 3n:** The brain of the project, the AI model itself.

---

## 🚀 Future Plans

* Implement a profile system to track user progress and past topics.
* Expand the number of supported languages and subjects.
* Leverage Gemma 3n's multimodal capabilities to generate images and diagrams to explain complex topics visually.

---

## 👤 Contact

**Harun Gökce**

* **GitHub:** [github.com/Harungokc](https://github.com/Harungokc)
* **LinkedIn:** [linkedin.com/in/www.linkedin.com/in/harun-gökce-08843a298](https://linkedin.com/in/www.linkedin.com/in/harun-gökce-08843a298)
* **Kaggle:** [kaggle.com/https://www.kaggle.com/harunngokce](https://kaggle.com/https://www.kaggle.com/harunngokce)