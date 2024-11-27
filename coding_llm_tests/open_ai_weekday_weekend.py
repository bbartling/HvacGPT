import os
import io
import sys
from datetime import datetime
from openai import OpenAI

# Retrieve OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    exit(1)

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Function to generate Python code
def generate_code(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace with your model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        generated_code = response.choices[0].message.content

        # Post-process to extract the Python code block
        code_lines = generated_code.splitlines()
        inside_code_block = False
        clean_code = []

        for line in code_lines:
            if line.strip().startswith("```python"):  # Start of code block
                inside_code_block = True
                continue
            elif line.strip().startswith("```"):  # End of code block
                inside_code_block = False
                continue
            if inside_code_block:
                clean_code.append(line)

        clean_code = "\n".join(clean_code).replace("’", "'")  # Replace invalid quotes
        return {"code": clean_code}
    except Exception as e:
        print(f"Error during code generation: {e}")
        exit(1)


# Function to validate and execute the generated code
def validate_and_execute(code_dict):
    captured_output = io.StringIO()
    sys.stdout = captured_output  # Redirect stdout
    try:
        print("Executing Generated Code:")
        print(code_dict["code"])  # Show the code being executed
        exec(code_dict["code"], {})  # Execute the code in a new namespace
        sys.stdout = sys.__stdout__  # Reset stdout
        return {
            "status": "success",
            "code": code_dict["code"],
            "output": captured_output.getvalue()
        }
    except Exception as e:
        sys.stdout = sys.__stdout__  # Reset stdout in case of error
        return {
            "status": "error",
            "error": str(e),
            "code": code_dict["code"]
        }
    
# Function to save generated code to a file
def save_code_to_file(code, filename="generated_script.py"):
    with open(filename, "w") as file:
        file.write(code)
    print(f"Generated code has been saved to {filename}")


# Function to analyze results using OpenAI
def ai_analyze_results(code, output):
    try:
        analysis_prompt = (
            f"The following Python code was executed:\n\n"
            f"```\n{code}\n```\n\n"
            f"It produced the following output:\n\n"
            f"```\n{output}\n```\n\n"
            f"Determine if the code worked as expected based on this context: "
            f"The script should print 'Hello, it’s a weekday' if it’s Monday to Friday, "
            f"and 'Hello, it’s the weekend' if it’s Saturday or Sunday. "
            f"Explain your reasoning and suggest improvements if needed."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Replace with your model
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during AI-driven analysis: {e}")
        return None

# Main function
if __name__ == "__main__":
    # Step 1: Generate the Python script
    prompt = (
        "Write a Python script that checks if today is a weekday or weekend. "
        "It should print 'Hello, it’s a weekday' if it’s Monday to Friday, "
        "and 'Hello, it’s the weekend' if it’s Saturday or Sunday."
    )
    generated = generate_code(prompt)
    print("\nGenerated Python Code:")
    print(generated["code"])

    # Save the generated code to a file
    save_code_to_file(generated["code"])

    # Step 2: Validate and execute the generated code
    print("\nValidating and executing the code...")
    result = validate_and_execute(generated)

    # Step 3: AI-driven analysis of the results
    if result["status"] == "success":
        print("\nCaptured Output from Execution:")
        print(result["output"])
        print("\nAnalyzing Results Using OpenAI...")
        ai_analysis = ai_analyze_results(result["code"], result["output"])
        print("\nAI Analysis:")
        print(ai_analysis)
    else:
        print("\nError occurred during execution:")
        print(result["error"])
