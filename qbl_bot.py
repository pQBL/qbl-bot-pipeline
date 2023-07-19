import os, sys, time, openai
from typing import List, Dict, Optional

# Dummy variables
unit = "Week 1: Intro to Golang & Basic Concurrency"
page_name = "Tour of Go 1 (Basics)"
skills = ["Understand and apply Golang fundamentals: Basic syntax",
          "Understand and apply Golang fundamentals: Types",
          "Understand and apply Golang fundamentals: Control structures"]

#
# Helper functions
#
def get_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY_KTH") 
    if not key:
        raise ValueError("Environment variable OPENAI_API_KEY is not set.")
    return key

# Filter out the chars in the given string
def filter_chars(string: str, chars_to_remove: str) -> str:
    return string.translate(str.maketrans("", "", chars_to_remove))

def create_message(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

# Add prompt string to messages and return response string
def fetch_response_content(prompt: str, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> str:
    messages.append(create_message("user", prompt))
    content = ""

    print("  Sending API request") # For debugging
    start_time = time.time()
    try:
        chat_completion = openai.ChatCompletion.create(
            model = model,
            messages = messages,
        )
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"  API request was successful (took {round(execution_time, 2)} seconds)") # For debugging
        content = chat_completion.choices[0].message.content
    except Exception as e:
        print("There was an issue fetching the API response:", e)
        sys.exit(1)

    return content

def questions_prompt(skill: str, number_of_questions: int) -> str:
    return f"""Your task is to create questions for a Question Based Learning (QBL) course.

    The course is an introduction to parallel and concurrent programming, and the programming language is Go / Golang. 

    Assume students have some programming experience in another language, such as Java or Python.

    Summary of QBL: ###
    QBL is about learning through answering questions. The focus is on learning, not evaluation.

    The underlying philosophy is: "If you know the answer to all the questions from the start, it would mean you had nothing to learn from the course."

    A course consists of learning goals.
    Learning goals consist of skills.
    Skills consist of questions.

    Questions consist of:
    1. The actual question
    2. Answer options
    3. Tailored feedback for each option

    Good questions should:
    * be easy to understand
    * focus on common misconceptions regarding the subject
    * encourage independent thinking ("understanding" or higher in Bloom's taxonomy)

    Good options should:
    * be easy to read (short and concise)
    * be reasonable and appropriate in context
    * be given in sets of three (or more, but three is optimal)

    Good feedback should:
    * begin with "Correct." or "Incorrect." as appropriate
    * be short (about two sentences) and constructive
    * provide a unique explanation for each option (including the correct one)
    * guide the student in the right direction when the option is incorrect
    * only reveal the answer for the correct option(!)
    ###

    Question format: ###
    Question 1:
    <question>

    A: <plausible answer option>
    <tab>Feedback: <unique feedback tailored to A), that does not reveal the answer if incorrect>

    B: <plausible answer option>
    Feedback: <unique feedback tailored to B), that does not reveal the answer if incorrect>

    C: <plausible answer option>
    Feedback: <unique feedback tailored to C), that does not reveal the answer if incorrect>
    ###

    Begin by generating a short but informative knowledge bank about the skill, with the most essential information.

    Skill: ###{skill}###

    End by generating {number_of_questions} questions of varying difficulty, and provide code snippets to make it more interesting.

    (Remember: Do not reveal the correct answer if an option is incorrect!)"""

def improvement_prompt() -> str:
    return """Your task is now to evaluate the questions by critiquing them thoroughly.

    First give an unordered bullet list of the critique. Focus on the things that would give the most improvement, not what is already good.

    Then, improve the questions based on the list.

    Mark the critique section with "CRITIQUE:" and the improved questions with "IMPROVED QUESTIONS:"."""

#
# Main function, generates a page file in the specified directory.
# The 3.5 model is cheaper, but use "gpt-4" for better results.
#
def generate_page(unit_name: str, page_name: str, skills: List[str], questions_per_skill: int = 5,
                  dst_dir: str = "course_content", model="gpt-3.5-turbo") -> Optional[str]:
    # Start timer
    start_time = time.time()

    # Setup
    openai.api_key = get_openai_key()

    unit_name_underscored = unit_name.replace(' ', '_').lower()
    page_name_underscored = page_name.replace(' ', '_').lower()

    file_name = f"{unit_name_underscored}-{page_name_underscored}"
    file_path = f"{dst_dir}/{file_name}"
    page_header = f"\n\nUnit: {unit_name}\nPage_name: {page_name}"

    illegal_chars_for_git_branch_names = r"~^:\*?[]@{}!"
    file_name = filter_chars(file_name, illegal_chars_for_git_branch_names)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    with open(file_path, 'a') as file:
        file.write(page_header)    

    # Produce questions
    print(f"\nGenerating page \"{page_name}\"")

    for skill in skills:
        context = "Your are a pedagogical professor in computer science, with 20+ years of experience."
        messages = [{"role": "system", "content": context}]

        questions = fetch_response_content(questions_prompt(skill, questions_per_skill), messages, model)
        # print(f"\n\nQuestions: \n\n{questions}") # For debugging
        messages.append(create_message("assistant", questions))

        critique_and_improved_questions = fetch_response_content(improvement_prompt(), messages, model)
        # print(f"\n\nImproved questions: \n\n{improved_questions}") # For debugging
        messages.append(create_message("assistant", critique_and_improved_questions))

        # Remove critique by splitting after the critique and selecting the second part of the split
        improved_questions_without_critique = critique_and_improved_questions.split("IMPROVED QUESTIONS:")[1].strip()
        # print(f"\n\nImproved questions: \n\n{improved_questions_without_critique}") # For debugging

        with open(file_path, 'a') as file:
            # print(f"\nPrinting the following to {file_name}:\n\n{improved_questions_without_critique}") # For debugging
            file.write(f"\n\n{improved_questions_without_critique}")

    # Print total time taken to generate page
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"  Time to generate: {round(execution_time, 2)} seconds")

    return file_path

# if __name__ == "__main__":
#     generate_page(unit, page_name, skills)
