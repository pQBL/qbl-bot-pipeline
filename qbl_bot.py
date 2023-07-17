import os
import sys
import openai

model = "gpt-3.5-turbo"
system_role = "Your are a pedagogical professor in computer science, with 20+ years of experience."
skill = "Understand the basics of concurrent, parallel, and sequential programming, and their differences."
number_of_questions = 3

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


improvement_test = """CRITIQUE:
- The questions could benefit from being more specific and targeted towards the differences between sequential, concurrent, and parallel programming.
- The feedback for incorrect options should provide more guidance and explanations to help students understand the reasoning behind the correct answer.
- The code snippet in Question 3 could be more challenging and related directly to concurrent or parallel programming concepts.

IMPROVED QUESTIONS:

Question 1:
What is the primary difference between sequential and concurrent programming?

A: Sequential programming executes tasks one after the other in a linear order, while concurrent programming allows tasks to overlap and execute simultaneously.
    Feedback: Correct. Sequential programming follows a strict linear order of execution, whereas concurrent programming allows for task overlap and simultaneous execution, leading to improved responsiveness and resource utilization.

B: Sequential programming executes tasks simultaneously, while concurrent programming executes tasks in a linear order.
    Feedback: Incorrect. Sequential programming does not involve simultaneous execution of tasks.

C: There is no difference; sequential and concurrent programming refer to the same approach.
    Feedback: Incorrect. Sequential and concurrent programming are distinct approaches with differences in execution order and task overlap.

Question 2:
Which programming approach is specifically designed to utilize multiple processor cores for faster execution of computationally intensive tasks?

A: Sequential programming
    Feedback: Incorrect. Sequential programming does not take advantage of multiple processor cores.

B: Concurrent programming
    Feedback: Incorrect. While concurrent programming can allow overlapping of tasks, it may not fully utilize the potential of multiple processor cores for faster execution of computationally intensive tasks.

C: Parallel programming
    Feedback: Correct. Parallel programming is specifically designed to leverage multiple processor cores, executing tasks simultaneously and achieving faster execution for computationally intensive tasks.

Question 3:
Consider the following code snippet:

```go
func main() {
    go func() {
        fmt.Println("Goroutine 1")
    }()
    
    fmt.Println("Main function")
}
```

What will be the output of the code?

A: Goroutine 1
    Feedback: Incorrect. The main function does not wait for the goroutine to finish executing before printing its output, so "Goroutine 1" may not be printed.

B: Main function
    Feedback: Correct. The main function executes before the goroutine, so "Main function" will be printed first.

C: Goroutine 1, Main function
    Feedback: Incorrect. The goroutine executes concurrently but may not necessarily complete before the main function. Therefore, "Goroutine 1" will not be printed before "Main function" in this specific code snippet.

Note: While the code snippet in this question may not directly reflect concurrent or parallel programming concepts, it does introduce the idea of goroutines and asynchronous execution, which can lead to further discussions on concurrency in Go."""

#
# Run script
#
def main(unit="unit1", page_name="page2", dst_dir="course_content"):
    # Setup
    openai.api_key = get_openai_key()
    messages = [{"role": "system", "content": system_role}]

    file_name = f"{unit.replace(' ', '_')}-{page_name.replace(' ', '_')}"
    file_path = f"{dst_dir}/{file_name}"
    page_header = f"Unit: {unit}\nPage_name: {page_name}\n\n"

    # TODO: make sure folder exists

    with open(file_path, 'a') as file:
        file.write(page_header)    

    # Initial prompt
    questions_prompt_message = create_message("user", question_prompt(skill, number_of_questions))

    messages.append(questions_prompt_message)
    # print("\nPrompt:\n\n", messages) # For debugging

    # Initial questions
    print("Questions prompt sent")
    questions_response = get_response_from_api(model, messages)
    questions_content = questions_response.choices[0].message.content
    questions_message = create_message("assistant", questions_content)

    messages.append(questions_message)
    # print("\nQuestions:\n\n", messages) # For debugging

    # Improvement prompt
    improvement_prompt_message = create_message("user", improvement_prompt())

    messages.append(improvement_prompt_message)
    # print("\nImprovement prompt:\n\n", messages) # For debugging

    # Improved questions
    print("Improvement prompt sent")
    improvement_response = get_response_from_api(model, messages)
    improvement_content = improvement_response.choices[0].message.content
    improvement_message = create_message("assistant", improvement_content)

    messages.append(improvement_message)
    # print("\nImproved questions:\n\n", messages) # For debugging

    split_improvement = improvement_content.split("IMPROVED QUESTIONS:")

    print(f"\n\nImproved split:\n\n{split_improvement}")

    # Save to file
    with open(file_path, 'a') as file:
        questions = split_improvement[1].strip()
        print(questions)
        file.write(questions)

    return file_name

if __name__ == "__main__":
    main()
