import os, sys, time, openai
from typing import List, Dict, Optional
from prompts import questions_prompt, improvement_prompt

role_preset = "Your are a pedagogical professor in computer science, with 20+ years of experience."
course_preset = """The course is an introduction to parallel and concurrent programming, and the programming language is Go / Golang. 

Assume students have some programming experience in another language, such as Java or Python.

Provide code snippets to make it more interesting, and format inline code as monospace."""

#
# Helper functions
#
def get_openai_key() -> str:
    key_name = "OPENAI_API_KEY_KTH"
    key = os.getenv(key_name) 
    if not key:
        raise ValueError(f"Environment variable {key_name} is not set.")
    return key

# Filter out the chars in the given string
def filter_chars(string: str, chars_to_remove: str) -> str:
    return string.translate(str.maketrans("", "", chars_to_remove))

def create_message(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

# Add prompt string to messages and return response string
def fetch_response_content(prompt: str, messages: List[Dict[str, str]], model: str, max_try_count: int = 2) -> str:
    messages.append(create_message("user", prompt))
    content = ""

    try_count = 0

    while try_count <= max_try_count:
        print("\n  Sending API request")  # For debugging
        start_time = time.time()
        try:
            chat_completion = openai.ChatCompletion.create(
                model=model,
                messages=messages,
            )
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"  Request was successful (took {round(execution_time, 2)} seconds)")  # For debugging
            content = chat_completion.choices[0].message.content
            break
        except Exception as e:
            try_count += 1
            print(f"  Attempt {try_count} of {max_try_count} failed\n  {e}")
            if try_count >= max_try_count:
                raise Exception(f"\n  (skipping page)")
            number_of_seconds_between_requests = 5
            print(f"  Waiting {number_of_seconds_between_requests} seconds before next request")
            time.sleep(number_of_seconds_between_requests)

    return content

#
# Main function, generates a page file in the specified directory.
# "gpt-3.5-turbo" is cheaper, but use "gpt-4" for better results.
#
def generate_page(unit_name: str, page_name: str, skills: List[str], questions_per_skill: int = 10,
                  dst_dir: str = "course_content", role_description: str = role_preset,
                  course_description: str = course_preset, model: str = "gpt-4") -> Optional[str]:
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
    print(f"\nGenerating page: \"{page_name}\"")
    print(f"Using GPT model: \"{model}\"")

    try: 
        for skill in skills:
            messages = [{"role": "system", "content": role_description}]

            questions = fetch_response_content(questions_prompt(course_description, skill, questions_per_skill), messages, model)
            messages.append(create_message("assistant", questions))

            critique_and_improved_questions = fetch_response_content(improvement_prompt(), messages, model)
            messages.append(create_message("assistant", critique_and_improved_questions))

            # Remove critique by splitting after the critique and selecting the second part of the split
            improved_questions_without_critique = critique_and_improved_questions.split("IMPROVED QUESTIONS:")[1].strip()

            # Append to file
            with open(file_path, 'a') as file:
                file.write(f"\n\n{improved_questions_without_critique}")
    except Exception as e:
        print(e)
        # Overwrite file and return
        with open(file_path, 'w') as file:
            file.write(f"REQUEST FAILED")
        return file_path


    # Print total time taken to generate page
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n  TIME TO GENERATE PAGE = {round(execution_time, 2)} seconds")

    return file_path
