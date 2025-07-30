from ollama import chat
import gradio as gr
import re
import json
import os

MODEL_NAME = "gemma3n"
DEFAULT_SETTINGS = {"temperature": 0.7, "timeout": 300}

# Global settings
current_topic = ""
current_lang = "en"  # Default language set to English
current_determined_level = ""
current_content_text = ""  # To store the explained content

# Level maps (Turkish to English and vice versa)
level_map_tr_to_en = {
    "Başlangıç": "Beginner",
    "Orta": "Intermediate",
    "İleri": "Advanced"
}
level_map_en_to_tr = {v: k for k, v in level_map_tr_to_en.items()}

# Global variables for quiz data
global_pre_quiz_data = []
global_post_quiz_data = []

# Global lists for UI components (for reset_app_state)
pre_quiz_components_ui = []
post_quiz_components_ui = []

# --- Global Dictionary for Text Translations ---
TEXTS = {
    "title": {"tr": "🧠 Kişiselleştirilmiş Öğrenme Asistanı", "en": "🧠 Personalized Learning Assistant"},
    "lang_choice": {"tr": "🌐 Dil Seçimi", "en": "🌐 Language Selection"},
    "topic_input_label": {"tr": "📝 Öğrenmek İstediğiniz Konu", "en": "📝 Topic You Want to Learn"},
    "topic_input_placeholder": {"tr": "Örn: Evrim Teorisi", "en": "E.g.: Theory of Evolution"},
    "start_quiz_btn": {"tr": "🚀 Seviye Belirleme Testini Başlat", "en": "🚀 Start Level Determination Quiz"},
    "pre_quiz_title": {"tr": "## 📋 Seviye Belirleme Testi", "en": "## 📋 Level Determination Quiz"},
    "pre_quiz_status_preparing": {"tr": "⏳ Seviye tespit sınavı hazırlanıyor...",
                                  "en": "⏳ Level determination quiz is being prepared..."},
    "pre_quiz_status_ready": {"tr": "✅ Sorular hazır! Lütfen cevaplayın.",
                              "en": "✅ Questions are ready! Please answer."},
    "pre_quiz_error_insufficient": {"tr": "⚠ Yeterli soru oluşturulamadı. Lütfen tekrar deneyin.",
                                    "en": "⚠ Not enough questions could be generated. Please try again."},
    "pre_quiz_error_general": {"tr": "🚨 Soru üretim hatası:", "en": "🚨 Question generation error:"},
    "submit_pre_quiz_btn": {"tr": "✅ Cevapları Değerlendir ve İlerle", "en": "✅ Evaluate Answers and Proceed"},
    "level_prefix": {"tr": "✅ Seviyeniz:", "en": "✅ Your Level:"},
    "content_tab_title": {"tr": "📖 Konu İçeriği", "en": "📖 Topic Content"},
    "references_tab_title": {"tr": "📚 Kaynaklar", "en": "📚 References"},
    "mini_quiz_tab_title": {"tr": "❓ Mini Quiz", "en": "❓ Mini Quiz"},
    "summary_preparing": {"tr": "⏳ Özet hazırlanıyor...", "en": "⏳ Summary is being prepared..."},
    "refs_preparing": {"tr": "⏳ Kaynaklar hazırlanıyor...", "en": "⏳ References are being prepared..."},
    "mini_quiz_preparing": {"tr": "⏳ Mini quiz hazırlanıyor...", "en": "⏳ Mini quiz is being prepared..."},
    "mini_quiz_ready": {"tr": "✅ Mini quiz hazır! Lütfen cevaplayın.", "en": "✅ Mini quiz is ready! Please answer."},
    "content_generation_error": {"tr": "🚨 İçerik üretim hatası:", "en": "🚨 Content generation error:"},
    "evaluate_quiz_btn": {"tr": "🎯 Quiz Sonuçlarını Göster", "en": "🎯 Show Quiz Results"},
    "quiz_result_calculating": {"tr": "⏳ Sonuçlar hesaplanıyor ve çözümler hazırlanıyor...",
                                "en": "⏳ Results are being calculated and solutions are being prepared..."},
    "quiz_result_correct": {"tr": "Soru {num}: ✅ Doğru!", "en": "Question {num}: ✅ Correct!"},
    "quiz_result_incorrect": {"tr": "Soru {num}: ❌ Yanlış. Doğru Cevap: {correct_key}) {correct_value}",
                              "en": "Question {num}: ❌ Incorrect. Correct Answer: {correct_key}) {correct_value}"},
    "explanation_prefix": {"tr": "   ℹ Açıklama:", "en": "   ℹ Explanation:"},
    "explanation_error": {"tr": "   🚨 Çözüm açıklaması alınamadı:",
                          "en": "   🚨 Solution explanation could not be retrieved:"},
    "overall_quiz_result": {"tr": "🎯 Mini Quiz Sonucu: {score}/{total} doğru.\n\n",
                            "en": "🎯 Mini Quiz Result: {score}/{total} correct.\n\n"},
    "quiz_success_msg": {"tr": "🎉 Tebrikler! {level} seviyesinde konuya hakimsiniz!",
                         "en": "🎉 Congratulations! You have mastered the topic at the {level} level!"},
    "quiz_improve_msg": {"tr": "📚 Harika çaba! Konuyu tekrar gözden geçirmek bilginizi pekiştirecektir.",
                         "en": "📚 Great effort! Reviewing the topic again will solidify your knowledge."},
    "back_to_start_btn": {"tr": "🏠 Ana Sayfaya Dön", "en": "🏠 Return to Home"},
    "llm_error": {"tr": "🚨 LLM Hatası:", "en": "🚨 LLM Error:"},
    "response_empty": {"tr": "⚠ Yanıt boş döndü.", "en": "⚠ Response returned empty."},
    "topic_qa_intro": {"tr": "### 💭 Yardım İsteyin", "en": "### 💭 Ask for Help"},
    "topic_qa_instruction": {"tr": "Yukarıda anlatılan konu ile ilgili sorularınızı buradan sorabilirsiniz.",
                             "en": "You can ask your questions about the topic explained above here."},
    "qa_input_label": {"tr": "Sorunuzu yazın", "en": "Type your question"},
    "qa_input_placeholder": {"tr": "Örn: Bu konunun en önemli noktaları neler?",
                             "en": "E.g.: What are the most important points of this topic?"},
    "qa_send_btn": {"tr": "Gönder", "en": "Send"},
    "qa_user_title": {"tr": "Siz", "en": "You"},
    "qa_assistant_title": {"tr": "Asistan", "en": "Assistant"},
    "qa_no_content": {"tr": "⚠ Henüz konu içeriği yüklenmedi.", "en": "⚠ Topic content not loaded yet."},
    "qa_off_topic": {"tr": "Bu soru '{topic}' konusu ile ilgili değil. Lütfen konu ile ilgili bir soru sorun.",
                     "en": "This question is not related to '{topic}'. Please ask a question about the topic."},
    "qa_not_enough_info": {"tr": "Bu konuda yukarıdaki içerikte yeterli bilgi bulunmuyor.",
                           "en": "There isn't sufficient information about this in the content above."},
    "qa_error_general": {"tr": "🚨 Soru yanıtlama hatası:", "en": "🚨 Question answering error:"},
    "ollama_conn_success": {"tr": "✅ Ollama bağlantısı başarılı.", "en": "✅ Ollama connection successful."},
    "ollama_conn_fail": {"tr": "❌ Ollama bağlantısı kurulamadı.", "en": "❌ Ollama connection failed."},
    "quiz_question_label": {"tr": "Soru", "en": "Question"},
}


def post_model(prompt, system, settings=None, stream=False):
    options = DEFAULT_SETTINGS.copy()
    if settings:
        options.update(settings)
    try:
        if stream:
            full_response = ""
            for chunk in chat(MODEL_NAME, messages=[system, {"role": "user", "content": prompt}], options=options,
                              stream=True):
                if "message" in chunk and "content" in chunk["message"]:
                    full_response += chunk["message"]["content"]
                    yield full_response
            if not full_response:
                yield TEXTS["response_empty"][current_lang]
        else:
            res = chat(MODEL_NAME, messages=[system, {"role": "user", "content": prompt}], options=options)
            if "message" in res and "content" in res["message"]:
                yield res["message"]["content"]
            else:
                yield TEXTS["response_empty"][current_lang]
    except Exception as e:
        yield f"{TEXTS['llm_error'][current_lang]} {e}"


def parse_questions_improved(llm_output, num_questions):
    questions_data = []
    lines = [line.strip() for line in llm_output.split('\n') if line.strip()]

    question_block_pattern = re.compile(
        r"(?:S|Q)(\d+)\.\s*(.+?)\n"
        r"([A-D]\)\s*.+?\n){4}"
        r"(?:Cevap|Answer|Doğru|Correct):\s*([A-D])",
        re.DOTALL | re.IGNORECASE
    )

    matches = question_block_pattern.finditer(llm_output)

    for match in matches:
        if len(questions_data) >= num_questions:
            break

        q_num = match.group(1)
        q_text = match.group(2).strip()
        correct_answer_key = match.group(match.lastindex).upper()

        option_lines = re.findall(r'([A-D])\)\s*(.+?)(?=\n[A-D]\)|\n(?:Cevap|Answer|Doğru|Correct):|$)', match.group(0),
                                  re.DOTALL | re.IGNORECASE)

        options = {}
        for opt_key, opt_value in option_lines:
            opt_key = opt_key.upper()
            opt_value = opt_value.strip()

            cleaned_opt_value = re.sub(r'\s*\(?(?:doğru|correct|cevap|answer)\s*[^)]*\)?', '', opt_value,
                                       flags=re.IGNORECASE).strip()

            if not cleaned_opt_value or cleaned_opt_value.lower() in ["cevap", "answer"]:
                options[opt_key] = ""
            else:
                options[opt_key] = cleaned_opt_value

        if len(options) != 4:
            print(f"Warning: Could not find 4 options for question {q_num}. Full output: \n{match.group(0)}")
            continue

        questions_data.append({
            "question_num": q_num,
            "question_text": q_text,
            "options": options,
            "correct_answer": correct_answer_key
        })

    return questions_data[:num_questions]


def create_structured_prompt(topic, lang, num_questions, level=""):
    """Creates a more structured prompt"""
    level_for_prompt = level_map_tr_to_en.get(level, level)

    if lang == "tr":
        return {
            "role": "system",
            "content": f"""Sen bir eğitim uzmanısın. '{topic}' konusu hakkında {num_questions} adet çoktan seçmeli soru oluşturacaksın.
KURALLARI SIKICA TAKİP ET:
1. Her soru tam olarak 4 seçenek (A, B, C, D) içermeli.
2. Her sorunun sonunda, yeni bir satırda, 'Cevap: X' formatında doğru şıkkı belirt.
3. Sorular {level} seviyesine uygun olmalı.
4. Format kesinlikle şu şekilde olmalı:

S1. [Soru metni]?
A) [Seçenek A]
B) [Seçenek B] 
C) [Seçenek C]
D) [Seçenek D]
Cevap: A

ÖNEMLİ: Şıkların içine parantez içinde ipucu EKLEME.
Bu formatı kesinlikle koru. Başka açıklama yapma."""
        }
    else:  # English
        return {
            "role": "system",
            "content": f"""You are an education expert. Create {num_questions} multiple-choice questions about '{topic}'.
FOLLOW THESE RULES STRICTLY:
1. Each question must have exactly 4 options (A, B, C, D).
2. At the end of each question, on a new line, specify the correct answer in 'Answer: X' format.
3. Questions should be appropriate for {level_for_prompt} level.
4. The format must be exactly as follows:

Q1. [Question text]?
A) [Option A]
B) [Option B]
C) [Option C] 
D) [Option D]
Answer: A

IMPORTANT: Do NOT add hints in parentheses inside the options.
Keep this format strictly. Do not add other explanations."""
        }


def generate_solution_explanation(question_data, user_answer_key, correct_answer_key, lang):
    q_text = question_data["question_text"]
    options_text = "\n".join([f"{k}) {v}" for k, v in question_data["options"].items()])
    correct_option_value = question_data["options"].get(correct_answer_key,
                                                        "Info not found." if lang == "en" else "Bilgi bulunamadı.")
    user_option_value = question_data["options"].get(user_answer_key,
                                                     "No answer given/found." if lang == "en" else "Cevap verilmedi/bulunamadı.")

    if lang == "tr":
        system_prompt = {
            "role": "system",
            "content": f"""Sen bir eğitim uzmanısın. Öğrenciye yanlış cevapladığı bir çoktan seçmeli sorunun doğru çözümünü açıklayacaksın. Açıklaman kısa ve anlaşılır olmalı, sorunun konusunu netleştirmeli. Cevap gerekçesini vurgula.

Soru: {q_text}
Şıklar:
{options_text}
Verilen Cevap: {user_answer_key}) {user_option_value}
Doğru Cevap: {correct_answer_key}) {correct_option_value}

Bu sorunun doğru cevabını, yukarıdaki bilgileri kullanarak, yanlış cevabın neden yanlış olduğunu da kısaca belirterek açıkla. Sadece açıklamayı yap, başlık veya ek bilgi verme."""
        }
    else:
        system_prompt = {
            "role": "system",
            "content": f"""You are an education expert. You will explain the correct solution to a multiple-choice question that the student answered incorrectly. Your explanation should be brief and clear, clarifying the subject of the question. Emphasize the reason for the answer.

Question: {q_text}
Options:
{options_text}
Given Answer: {user_answer_key}) {user_option_value}
Correct Answer: {correct_answer_key}) {correct_option_value}

Explain the correct answer to this question, using the information above, briefly stating why the given answer was incorrect. Provide only the explanation, no titles or extra information."""
        }

    return next(post_model(q_text, system_prompt, settings={"temperature": 0.5}, stream=False))


def generate_pre_quiz_questions(topic, lang):
    global current_topic, global_pre_quiz_data, current_lang
    current_topic = topic
    current_lang = lang
    global_pre_quiz_data = []

    system_prompt = create_structured_prompt(topic, lang, 3)

    yield TEXTS["pre_quiz_status_preparing"][current_lang], *[gr.update() for _ in range(6)]

    try:
        full_response = ""
        for chunk in post_model(topic, system_prompt, stream=True):
            full_response = chunk

        global_pre_quiz_data = parse_questions_improved(full_response, 3)

        if len(global_pre_quiz_data) < 3:
            error_msg = TEXTS["pre_quiz_error_insufficient"][current_lang]
            yield error_msg, *[gr.update(visible=False) for _ in range(6)]
            return

        updates = []
        for i, q_data in enumerate(global_pre_quiz_data):
            options = [f"{k}) {v}" for k, v in q_data["options"].items()]
            updates.extend([
                gr.update(value=f"{q_data['question_num']}. {q_data['question_text']}", visible=True),
                gr.update(label=f"{TEXTS['quiz_question_label'][current_lang]} {i + 1}", choices=options, value=None,
                          visible=True, interactive=True)
            ])

        while len(updates) < 6: updates.append(gr.update(visible=False))

        yield TEXTS["pre_quiz_status_ready"][current_lang], *updates

    except Exception as e:
        yield f"{TEXTS['pre_quiz_error_general'][current_lang]} {e}", *[gr.update(visible=False) for _ in range(6)]


def evaluate_pre_quiz_and_generate_content(*answers):
    global current_determined_level, global_post_quiz_data, current_content_text, current_lang

    score = sum(1 for i, ans in enumerate(answers) if
                i < len(global_pre_quiz_data) and ans and ans.startswith(global_pre_quiz_data[i]['correct_answer']))

    if score >= 2:
        current_determined_level = "İleri" if current_lang == "tr" else "Advanced"
    elif score == 1:
        current_determined_level = "Orta" if current_lang == "tr" else "Intermediate"
    else:
        current_determined_level = "Başlangıç" if current_lang == "tr" else "Beginner"

    level_msg = f"{TEXTS['level_prefix'][current_lang]} {current_determined_level}."

    def empty_updates(count):
        return [gr.update() for _ in range(count)]

    try:
        summary_text = ""
        yield level_msg, TEXTS["summary_preparing"][current_lang], "", "", "", *empty_updates(20)

        llm_level = level_map_tr_to_en.get(current_determined_level, current_determined_level)

        summary_system = {"role": "system",
                          "content": f"Explain the topic '{current_topic}' to someone at a '{llm_level}' level. Use {current_lang} language."}

        for chunk in post_model(current_topic, summary_system, stream=True):
            summary_text = chunk
            current_content_text = summary_text
            yield level_msg, summary_text, "", "", "", *empty_updates(20)

        refs_text = ""
        yield level_msg, summary_text, TEXTS["refs_preparing"][current_lang], "", "", *empty_updates(20)
        refs_system = {"role": "system",
                       "content": f"Suggest 3 reliable sources for '{current_topic}' in {current_lang} language."}
        for chunk in post_model(current_topic, refs_system, stream=True):
            refs_text = chunk
            yield level_msg, summary_text, refs_text, "", "", *empty_updates(20)

        yield level_msg, summary_text, refs_text, TEXTS["mini_quiz_preparing"][current_lang], "", *empty_updates(20)
        quiz_system = create_structured_prompt(current_topic, current_lang, 10, current_determined_level)
        quiz_response = next(post_model(current_topic, quiz_system))
        global_post_quiz_data = parse_questions_improved(quiz_response, 10)

        if len(global_post_quiz_data) < 10:
            raise ValueError(TEXTS["pre_quiz_error_insufficient"][current_lang])

        post_quiz_updates = []
        for i, q_data in enumerate(global_post_quiz_data):
            options = [f"{k}) {v}" for k, v in q_data["options"].items()]
            post_quiz_updates.extend(
                [gr.update(value=f"{q_data['question_num']}. {q_data['question_text']}", visible=True),
                 gr.update(label=f"{TEXTS['quiz_question_label'][current_lang]} {i + 1}", choices=options, value=None,
                           visible=True, interactive=True)])

        while len(post_quiz_updates) < 20: post_quiz_updates.append(gr.update(visible=False))

        final_quiz_status = TEXTS["mini_quiz_ready"][current_lang]

        empty_textbox = gr.update(value="", interactive=True)

        yield level_msg, summary_text, refs_text, final_quiz_status, empty_textbox, *post_quiz_updates

    except Exception as e:
        yield level_msg, f"{TEXTS['content_generation_error'][current_lang]} {e}", "", "", gr.update(
            value=""), *empty_updates(20)


def evaluate_mini_quiz(*answers):
    global global_post_quiz_data, current_lang

    yield TEXTS["quiz_result_calculating"][current_lang]

    score = 0
    total = len(global_post_quiz_data)

    result_text_parts = []

    for i, user_ans in enumerate(answers):
        if i >= total:
            break

        q_data = global_post_quiz_data[i]
        question_num = q_data["question_num"]
        correct_answer_key = q_data["correct_answer"]

        user_answer_cleaned = user_ans[0] if user_ans and len(user_ans) > 0 else ""

        if user_answer_cleaned == correct_answer_key:
            score += 1
            result_text_parts.append(TEXTS["quiz_result_correct"][current_lang].format(num=question_num))
        else:
            result_text_parts.append(
                TEXTS["quiz_result_incorrect"][current_lang].format(
                    num=question_num,
                    correct_key=correct_answer_key,
                    correct_value=q_data['options'].get(correct_answer_key,
                                                        ('Unknown' if current_lang == 'en' else 'Bilinmiyor'))
                )
            )

            try:
                explanation = generate_solution_explanation(q_data, user_answer_cleaned, correct_answer_key,
                                                            current_lang)
                result_text_parts.append(f"    {TEXTS['explanation_prefix'][current_lang]} {explanation}")
            except Exception as e:
                result_text_parts.append(f"    {TEXTS['explanation_error'][current_lang]} {e}")

        result_text_parts.append("\n")

    overall_result = TEXTS["overall_quiz_result"][current_lang].format(score=score, total=total)

    display_level_for_msg = current_determined_level
    if current_lang == "en":
        display_level_for_msg = level_map_tr_to_en.get(current_determined_level, current_determined_level)

    if score / total >= 0.7:
        overall_result += TEXTS["quiz_success_msg"][current_lang].format(level=display_level_for_msg)
    else:
        overall_result += TEXTS["quiz_improve_msg"][current_lang]

    final_output = overall_result + "\n\n" + "\n".join(result_text_parts)

    yield final_output


def check_ollama_connection():
    try:
        chat(MODEL_NAME, messages=[{"role": "user", "content": "test"}], options={"timeout": 10})
        return True
    except Exception:
        return False


def reset_app_state():
    global current_topic, current_lang, current_determined_level, global_pre_quiz_data, global_post_quiz_data, current_content_text, pre_quiz_components_ui, post_quiz_components_ui
    current_topic = ""
    current_lang = "en"
    current_determined_level = ""
    current_content_text = ""
    global_pre_quiz_data = []
    global_post_quiz_data = []

    # Reset UI components to their initial state
    updates = [
        gr.update(value="en"),  # Set dropdown to English
        gr.update(value="", interactive=True,
                  label=TEXTS["topic_input_label"]["en"], placeholder=TEXTS["topic_input_placeholder"]["en"]),
        gr.update(visible=True),  # topic_section
        gr.update(visible=False),  # pre_quiz_section
        gr.update(visible=False),  # content_section
        gr.update(visible=False),  # result_section. This should be false, not true.
        gr.update(value="", label=TEXTS["pre_quiz_status_preparing"]["en"]),
        # status_msg_pre_quiz initial value and label
        gr.update(value="", label=TEXTS["level_prefix"]["en"]),  # level_display initial value and label
        gr.update(value=""),  # content_display
        gr.update(value=""),  # references_display
        gr.update(value="", label=TEXTS["mini_quiz_preparing"]["en"]),  # quiz_status initial value and label
        gr.update(value=""),  # quiz_result
        gr.update(value="", interactive=True,
                  label=TEXTS["qa_input_label"]["en"], placeholder=TEXTS["qa_input_placeholder"]["en"]),
        # qa_input initial value, label, placeholder
        gr.update(value=""),  # qa_output_display (assuming this is the display for QA responses)
        gr.update(value=TEXTS["topic_qa_intro"]["en"]),  # qa_intro_markdown
        gr.update(value=TEXTS["topic_qa_instruction"]["en"]),  # qa_instruction_markdown
    ]

    # Reset pre_quiz_components (Markdown and Radio) in their interleaved order
    for comp in pre_quiz_components_ui:
        if isinstance(comp, gr.Markdown):
            updates.append(gr.update(visible=False, value="", label=""))
        elif isinstance(comp, gr.Radio):
            updates.append(gr.update(visible=False, value=None, choices=[], label=""))

    # Reset post_quiz_components (Markdown and Radio) in their interleaved order
    for comp in post_quiz_components_ui:
        if isinstance(comp, gr.Markdown):
            updates.append(gr.update(visible=False, value="", label=""))
        elif isinstance(comp, gr.Radio):
            updates.append(gr.update(visible=False, value=None, choices=[], label=""))

    return updates


def handle_question_submit(question):
    global current_content_text, current_topic, current_lang

    if not question.strip():
        yield current_content_text, ""
        return

    if not current_content_text:
        yield current_content_text, TEXTS["qa_no_content"][current_lang]
        return

    llm_level = level_map_tr_to_en.get(current_determined_level, current_determined_level)

    system_prompt = {
        "role": "system",
        "content": f"""You are an expert educational assistant on '{current_topic}'.

TOPIC CONTENT:
{current_content_text}

RULES:
1. ONLY answer questions DIRECTLY related to the above topic content and '{current_topic}'.
2. For off-topic questions, respond in {current_lang} with: "{TEXTS['qa_off_topic'][current_lang].format(topic=current_topic)}".
3. Base your answers on the above content, don't add your own knowledge.
4. Use clear, understandable, and educational language.
5. If unsure, say in {current_lang} with: "{TEXTS['qa_not_enough_info'][current_lang]}".
6. Level: {llm_level} - Explain appropriately for this level.
7. Respond in {current_lang} language."""
    }

    user_title = TEXTS["qa_user_title"][current_lang]
    assistant_title = TEXTS["qa_assistant_title"][current_lang]

    question_string = f"""
---
🧑‍💻 {user_title}: {question}

🤖 {assistant_title}: """

    yield current_content_text + question_string, ""

    full_response = ""
    try:
        for partial_response in post_model(question, system_prompt, settings={"temperature": 0.3}, stream=True):
            full_response = partial_response
            yield current_content_text + question_string + full_response, ""
    except Exception as e:
        error_msg = f"{TEXTS['qa_error_general'][current_lang]} {e}"
        yield current_content_text + question_string + error_msg, ""
        full_response = error_msg

    current_content_text += question_string + full_response


def build_ui():
    global pre_quiz_components_ui, post_quiz_components_ui
    with gr.Blocks(title=TEXTS["title"][current_lang], theme=gr.themes.Soft()) as demo:
        html_title = gr.HTML(f"<h1 style='text-align:center; color: #2563eb;'>{TEXTS['title'][current_lang]}</h1>")

        with gr.Column(visible=True) as topic_section:
            lang_dropdown = gr.Dropdown(["tr", "en"], value="en", label=TEXTS["lang_choice"][current_lang],
                                        interactive=True)
            topic_input = gr.Textbox(label=TEXTS["topic_input_label"][current_lang],
                                     placeholder=TEXTS["topic_input_placeholder"][current_lang])
            start_btn = gr.Button(TEXTS["start_quiz_btn"][current_lang], variant="primary")

        with gr.Column(visible=False) as pre_quiz_section:
            pre_quiz_markdown_title = gr.Markdown(TEXTS["pre_quiz_title"][current_lang])
            status_msg_pre_quiz = gr.Markdown()
            for i in range(3):
                q_md = gr.Markdown(visible=False)
                q_radio = gr.Radio(label=f"{TEXTS['quiz_question_label'][current_lang]} {i + 1}", visible=False)
                pre_quiz_components_ui.extend([q_md, q_radio])
            submit_pre_quiz_btn = gr.Button(TEXTS["submit_pre_quiz_btn"][current_lang], variant="secondary")

        with gr.Column(visible=False) as content_section:
            level_display = gr.Markdown()
            with gr.Tabs() as content_tabs:
                with gr.TabItem(TEXTS["content_tab_title"][current_lang]) as content_tab_item:
                    content_display = gr.Markdown()

                    qa_intro_markdown = gr.Markdown(TEXTS["topic_qa_intro"][current_lang])
                    qa_instruction_markdown = gr.Markdown(TEXTS["topic_qa_instruction"][current_lang])

                    with gr.Row():
                        qa_input = gr.Textbox(
                            label=TEXTS["qa_input_label"][current_lang],
                            placeholder=TEXTS["qa_input_placeholder"][current_lang],
                            lines=2,
                            interactive=True,
                            scale=4
                        )
                        qa_btn = gr.Button(
                            value=TEXTS["qa_send_btn"][current_lang],
                            variant="primary",
                            scale=1,
                            min_width=0
                        )
                    # This component will display the assistant's answer for QA
                    qa_output_display = gr.Markdown()

                with gr.TabItem(TEXTS["references_tab_title"][current_lang]) as references_tab_item:
                    references_display = gr.Markdown()
                with gr.TabItem(TEXTS["mini_quiz_tab_title"][current_lang]) as mini_quiz_tab_item:
                    quiz_status = gr.Markdown()
                    for i in range(10):
                        p_q_md = gr.Markdown(visible=False)
                        p_q_radio = gr.Radio(label=f"{TEXTS['quiz_question_label'][current_lang]} {i + 1}",
                                             visible=False)
                        post_quiz_components_ui.extend([p_q_md, p_q_radio])
                    evaluate_quiz_btn = gr.Button(TEXTS["evaluate_quiz_btn"][current_lang], variant="secondary")

        with gr.Column(visible=False) as result_section:
            quiz_result = gr.Markdown()
            back_to_start_btn = gr.Button(TEXTS["back_to_start_btn"][current_lang], variant="primary")

        def update_ui_language(selected_lang):
            global current_lang
            current_lang = selected_lang

            updated_html_title = f"<h1 style='text-align:center; color: #2563eb;'>{TEXTS['title'][selected_lang]}</h1>"

            updates = [
                gr.update(value=updated_html_title),
                gr.update(label=TEXTS["lang_choice"][selected_lang]),
                gr.update(label=TEXTS["topic_input_label"][selected_lang],
                          placeholder=TEXTS["topic_input_placeholder"][selected_lang]),
                gr.update(value=TEXTS["start_quiz_btn"][selected_lang]),
                gr.update(value=TEXTS["pre_quiz_title"][selected_lang]),
                gr.update(value=TEXTS["submit_pre_quiz_btn"][selected_lang]),
                gr.update(label=TEXTS["content_tab_title"][selected_lang]),
                gr.update(label=TEXTS["references_tab_title"][selected_lang]),
                gr.update(label=TEXTS["mini_quiz_tab_title"][selected_lang]),
                gr.update(value=TEXTS["evaluate_quiz_btn"][selected_lang]),
                gr.update(value=TEXTS["back_to_start_btn"][selected_lang]),
                gr.update(value=TEXTS["topic_qa_intro"][selected_lang]),
                gr.update(value=TEXTS["topic_qa_instruction"][selected_lang]),
                gr.update(label=TEXTS["qa_input_label"][selected_lang],
                          placeholder=TEXTS["qa_input_placeholder"][selected_lang]),
                gr.update(value=TEXTS["qa_send_btn"][selected_lang]),
            ]

            for i in range(3):
                updates.append(gr.update(label=f"{TEXTS['quiz_question_label'][selected_lang]} {i + 1}"))
            for i in range(10):
                updates.append(gr.update(label=f"{TEXTS['quiz_question_label'][selected_lang]} {i + 1}"))

            return updates

        lang_dropdown.change(
            fn=update_ui_language,
            inputs=[lang_dropdown],
            outputs=[
                html_title,
                lang_dropdown, topic_input, start_btn,
                pre_quiz_markdown_title, submit_pre_quiz_btn,
                content_tab_item, references_tab_item, mini_quiz_tab_item,
                evaluate_quiz_btn,
                back_to_start_btn,
                qa_intro_markdown,
                qa_instruction_markdown,
                qa_input,
                qa_btn,
                *[comp for comp in pre_quiz_components_ui if isinstance(comp, gr.Radio)],
                *[comp for comp in post_quiz_components_ui if isinstance(comp, gr.Radio)]
            ]
        )

        start_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            outputs=[topic_section, pre_quiz_section]
        ).then(
            fn=generate_pre_quiz_questions,
            inputs=[topic_input, lang_dropdown],
            outputs=[status_msg_pre_quiz, *pre_quiz_components_ui]
        )

        submit_pre_quiz_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            outputs=[pre_quiz_section, content_section]
        ).then(
            fn=evaluate_pre_quiz_and_generate_content,
            inputs=[comp for i, comp in enumerate(pre_quiz_components_ui) if i % 2 == 1],
            outputs=[level_display, content_display, references_display, quiz_status, qa_input,
                     *post_quiz_components_ui]
        )

        evaluate_quiz_btn.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            outputs=[content_section, result_section]
        ).then(
            fn=evaluate_mini_quiz,
            inputs=[comp for i, comp in enumerate(post_quiz_components_ui) if i % 2 == 1],
            outputs=[quiz_result]
        )

        qa_input.submit(
            fn=handle_question_submit,
            inputs=[qa_input],
            outputs=[content_display, qa_output_display]  # Changed to qa_output_display
        )

        qa_btn.click(
            fn=handle_question_submit,
            inputs=[qa_input],
            outputs=[content_display, qa_output_display]  # Changed to qa_output_display
        )

        back_to_start_btn.click(
            fn=reset_app_state,
            inputs=[],
            outputs=[
                lang_dropdown, topic_input, topic_section, pre_quiz_section, content_section, result_section,
                status_msg_pre_quiz, level_display, content_display, references_display, quiz_status, quiz_result,
                qa_input, qa_output_display, qa_intro_markdown, qa_instruction_markdown,
                *pre_quiz_components_ui,  # Changed from specific filtering to direct list expansion
                *post_quiz_components_ui  # Changed from specific filtering to direct list expansion
            ]
        )

    return demo


if __name__ == "__main__":
    if check_ollama_connection():
        print(TEXTS["ollama_conn_success"][current_lang])
    else:
        print(TEXTS["ollama_conn_fail"][current_lang])
    demo = build_ui()
    demo.launch(share=True)
