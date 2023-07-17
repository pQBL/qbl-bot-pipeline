import os
import sys
import openai

model = "gpt-3.5-turbo"
system_role = "Your are a pedagogical professor in computer science, with 20+ years of experience."
skill = "Understand the basics of concurrent, parallel, and sequential programming, and their differences."
number_of_questions = 5

#
# Helper functions
#
def get_openai_key():
    key = os.getenv("OPENAI_API_KEY") 
    if not key:
        raise ValueError("Environment variable OPENAI_API_KEY is not set.")
    return key

def create_message(role, content):
    return {"role": role, "content": content}

def get_response_from_api(model, messages):
    try:
        chat_completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            # temperature=0.1
        )
        return chat_completion
    except Exception as e:
        print("There was an issue fetching the API response:", e)
        sys.exit(1)

# def write_response(destination, data):
#     with open(destination, 'a') as file:
#         file.write("\n\n--- NEW RESPONSE ---\n\n")
#         file.write(data)
#     return

#
# Prompt functions
#
def questions_prompt(skill, number_of_questions):
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

def improvement_prompt():
    return """Your task is now to evaluate the questions by critiquing them thoroughly.

    First give an unordered bullet list of the critique. Focus on the things that would give the most improvement, not what is already good.

    Then, improve the questions based on the list.

    Mark the critique section with "CRITIQUE:" and the improved questions with "IMPROVED QUESTIONS:"."""


# Add prompt to messages and get response content
def fetch_response_content(prompt, messages):
    messages.append(create_message("user", prompt))
    content = ""

    print("Sending request")
    try:
        chat_completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )
        print("Request was successful")
        content = chat_completion.choices[0].message.content
    except Exception as e:
        print("There was an issue fetching the API response:", e)
        sys.exit(1)

    return content

#
# Run script
#
# TODO fix all parameters to main()
def main(unit="unit1", page_name="page2", dst_dir="course_content"):
    # Setup
    openai.api_key = get_openai_key()

    file_name = f"{unit.replace(' ', '_')}-{page_name.replace(' ', '_')}"
    file_path = f"{dst_dir}/{file_name}"
    page_header = f"Unit: {unit}\nPage_name: {page_name}\n\n"

    # TODO make sure folder exists
    with open(file_path, 'a') as file:
        file.write(page_header)    

    # Generate questions
    messages = [{"role": "system", "content": system_role}]

    questions = fetch_response_content(questions_prompt(skill, number_of_questions), messages)
    # print(f"\n\nQuestions: \n\n{questions}") # For debugging
    messages.append(create_message("assistant", questions))

    critique_and_improved_questions = fetch_response_content(improvement_prompt(), messages)
    # print(f"\n\nImproved questions: \n\n{improved_questions}") # For debugging
    messages.append(create_message("assistant", critique_and_improved_questions))

    improved_questions_without_critique = critique_and_improved_questions.split("IMPROVED QUESTIONS:")[1].strip()
    # print(f"\n\nImproved questions: \n\n{improved_questions_without_critique}") # For debugging

    # Save to file
    with open(file_path, 'a') as file:
        print(f"\nPrinting the following to {file_name}:\n\n{improved_questions_without_critique}")
        file.write(improved_questions_without_critique)

    return file_name

if __name__ == "__main__":
    main()
