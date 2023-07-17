import os
import sys
import openai

model = "gpt-3.5-turbo"
system_role = "Your are a pedagogical professor in computer science, with 20+ years of experience."
skill = "Understand the basics of concurrent, parallel, and sequential programming, and their differences."
number_of_questions = 10

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

def write_response(destination, data):
    with open(destination, 'a') as file:
        file.write("\n\n--- NEW RESPONSE ---\n\n")
        file.write(data)
    return

#
# Prompt functions
#
def question_prompt(skill, number_of_questions):
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
        **Question 1:**
        <question>

        **Options:**
        **A)** <plausible answer option>
        **B)** <plausible answer option>
        **C)** <plausible answer option>

        **Feedback:**
        **A)** <unique feedback tailored to A), that does not reveal the answer if incorrect>
        **B)** <unique feedback tailored to B), that does not reveal the answer if incorrect>
        **C)** <unique feedback tailored to C), that does not reveal the answer if incorrect>
        ###

        Begin by generating a short but informative knowledge bank about the skill, with the most essential information.

        Skill: ###{skill}###

        End by generating {number_of_questions} questions of varying difficulty, and provide code snippets to make it more interesting.

        (Remember: Do not reveal the correct answer if an option is incorrect!)"""

def improvement_prompt():
    return """Your task is now to evaluate the questions by critiquing them thoroughly.

        First give a bullet list of the critique. Focus on the things that would give the most improvement, not what is already good.

        Then, improve the questions based on the list."""

#
# Run script
#
def main():
    # Setup
    openai.api_key = get_openai_key()
    messages = [{"role": "system", "content": system_role}]
    
    # Initial prompt
    questions_prompt_message = create_message("user", question_prompt(skill, number_of_questions))

    messages.append(questions_prompt_message)
    print("\nPrompt:\n\n", messages) # For debugging

    # Initial questions
    questions_response = get_response_from_api(model, messages)
    questions_content = questions_response.choices[0].message.content
    questions_message = create_message("assistant", questions_content)

    messages.append(questions_message)
    print("\nQuestions:\n\n", messages) # For debugging

    # Improvement prompt
    improvement_prompt_message = create_message("user", improvement_prompt())

    messages.append(improvement_prompt_message)
    print("\nImprovement prompt:\n\n", messages) # For debugging

    # Improved questions
    improvement_response = get_response_from_api(model, messages)
    improvement_content = improvement_response.choices[0].message.content
    improvement_message = create_message("assistant", improvement_content)

    messages.append(improvement_message)
    print("\nImproved questions:\n\n", messages) # For debugging

    # Save to file
    write_response("response.md", improvement_content)

if __name__ == "__main__":
    main()
