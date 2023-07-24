def questions_prompt(course_description:str, skill: str, number_of_questions: int) -> str:
    return f"""Your task is to create questions for a Question Based Learning (QBL) course.

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

Course description: ###{course_description}###

Skill: ###{skill}###

Begin by generating a short but informative knowledge bank about the skill, with the most essential information.

End by generating {number_of_questions} questions of varying difficulty, and provide code snippets to make it more interesting.

It is very important that you do not cut off the response, even if the questions are very similar!

(Remember: Do not reveal the correct answer if an option is incorrect!)"""

def improvement_prompt() -> str:
    return """Your task is now to evaluate the questions by critiquing them thoroughly.

First give an unordered bullet list of the critique. Focus on the things that would give the most improvement, not what is already good.

Then, improve the questions based on the list.

Mark the critique section with "CRITIQUE:" and the improved questions with "IMPROVED QUESTIONS:".

In the final output, make sure to separate the end of one question from the beginning of another with 2 blank lines (2 line breaks)."""
