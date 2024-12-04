from openai import OpenAI
import os
from dotenv import load_dotenv
import json
load_dotenv()

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  
)

def read_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def query_gpt(prompt, model="gpt-4o-mini", max_tokens=500):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an assistant that extracts specific data fields from academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error querying GPT: {e}")
        return None
    
def process_markdown_with_gpt(markdown_content, questions):
    extracted_data = {}
    for question in questions:
        print(f"Processing: {question}")
        prompt = f"Based on the following academic paper content:\n\n{markdown_content}\n\n{question}"
        response = query_gpt(prompt)
        extracted_data[question] = response
    return extracted_data

def main():
    markdown_file = "/data/zhuanghao/rp/test2/[AR] -2011 - Investor Trading and the Post-Earnings-Announcement Drift/[AR] -2011 - Investor Trading and the Post-Earnings-Announcement Drift.md"
    output_dir = "output_dir"
    os.makedirs(output_dir, exist_ok=True)
    markdown_content = read_markdown(markdown_file)

    questions = [
        "What is the Title of the paper?",
        "Who are the Authors of the paper?",
        "What is the Publication Year?",
        "What is the Journal Name?",
        "What is the DOI or link to the paper?",
        "What are the Research Objectives of the paper (as mentioned in the abstract)?",
        "What are the Key Findings of the paper (as mentioned in the abstract)?",
        "What is the research methodology? Is it based on event study?",
        "What data sources are used in the paper?",
        "How are earnings announcements or events defined and measured?",
        "What are the sample characteristics such as time period and sample firms?",
        "What are the key dependent variables analyzed (Y, e.g., abnormal returns, trading volume)?",
        "What are the key covariates (X) used for regression or subsets?"
    ]

    extracted_data = process_markdown_with_gpt(markdown_content, questions)

    json_data = json.dumps(extracted_data, indent=2)
    output_file = os.path.join(output_dir, "extracted_data.json")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(json_data)

    print(f"Extraction complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()