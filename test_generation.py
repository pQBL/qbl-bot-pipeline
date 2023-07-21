import qbl_bot, time

# Page info
unit = "Week 1: Intro to Golang & Basic Concurrency"
pages = [{"title": "What is parallelism and concurrency?",
          "skills": ["Understand the basics of concurrency, parallelism and  sequential programming."]},
         {"title": "How is Go different from other programming languages?",
          "skills": ["Setup a functioning Go environment and set up Go modules."]},
         {"title": "Tour of Go 3 (Functions)",
          "skills": ["Understand and apply Golang fundamentals: Functions",
                     "Understand and apply Golang fundamentals: Variadic parameter functions",
                     "Understand and apply Golang fundamentals: Closures",
                     "Understand and apply Golang fundamentals: Anonymous functions"]}]


# Start timer
start_time = time.time()

# Generate pages
for page in pages:
    qbl_bot.generate_page(unit, page["title"], page["skills"], model="gpt-3.5-turbo")

# Print total time to generate all pages
end_time = time.time()
execution_time = end_time - start_time
print(f"\nTotal time to generate all pages: {round(execution_time / 60, 2)} minutes (= {round(execution_time, 2)} seconds)\n")