import os, sys, time, openai
from typing import List, Dict, Optional

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

You will be given contextual information wrapped in triple hash-symbols (###).

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
* be given in sets of three

Good feedback should:
* begin with "Correct." or "Incorrect." as appropriate
* be short (about two sentences) and constructive
* provide a unique explanation for each option (including the correct one)
* guide the student in the right direction when the option is incorrect
* only reveal the answer for the correct option(!)
###

Each entry should be a question with answer alternatives and each answer alternative should have feedback attached as a subpoint. This should be provided in a list format.

Question format: ###
<question number, a single digit starting with 1>. <question>

    A) <plausible answer option>
    - <unique feedback tailored to A), that does not reveal the answer if incorrect>
  
    B)  <plausible answer option>
    - <unique feedback tailored to B), that does not reveal the answer if incorrect>

    C)  <plausible answer option>
    - <unique feedback tailored to C), that does not reveal the answer if incorrect>
###

Begin by generating a short but informative knowledge bank about the skill, with the most essential information.

Skill: ###{skill}###

End by generating {number_of_questions} questions of varying difficulty, and provide code snippets to make it more interesting.

Format inline code as monospace.

(Remember: Do not reveal the correct answer if an option is incorrect!)"""

def improvement_prompt() -> str:
    return """Your task is now to evaluate the questions by critiquing them thoroughly.

First give an unordered bullet list of the critique. Focus on the things that would give the most improvement, not what is already good.

Then, improve the questions based on the list.

Mark the critique section with "CRITIQUE:" and the improved questions with "IMPROVED QUESTIONS:".

In the final output, make sure to separate the end of one question from the beginning of another with 2 blank lines (2 line breaks)."""

#
# Main function, generates a page file in the specified directory.
# "gpt-3.5-turbo" is cheaper, but use "gpt-4" for better results.
#
def generate_page(unit_name: str, page_name: str, skills: List[str], questions_per_skill: int = 10,
                  dst_dir: str = "course_content", model="gpt-4") -> Optional[str]:
    # Start timer
    start_time = time.time()

    # Setup
    openai.api_key = get_openai_key()

    unit_name_underscored = unit_name.replace(' ', '_').lower()
    page_name_underscored = page_name.replace(' ', '_').lower()

    file_name = f"{unit_name_underscored}-{page_name_underscored}"
    file_path = f"{dst_dir}/{file_name}"
    page_header = f"Unit_name: {unit_name}\nPage_name: {page_name}"

    illegal_chars_for_git_branch_names = r"~^:\*?[]@{}!"

    for c in illegal_chars_for_git_branch_names:
        file_path = file_path.replace(c, '')

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
        messages.append(create_message("assistant", questions))

        critique_and_improved_questions = fetch_response_content(improvement_prompt(), messages, model)
        messages.append(create_message("assistant", critique_and_improved_questions))

        # Remove critique by splitting after the critique and selecting the second part of the split
        improved_questions_without_critique = critique_and_improved_questions.split("IMPROVED QUESTIONS:")[1].strip()

        with open(file_path, 'a') as file:
            file.write(f"\n\n{improved_questions_without_critique}")

    # Print total time taken to generate page
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"  Time to generate: {round(execution_time, 2)} seconds")

    return file_path
