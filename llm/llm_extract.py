from openai import OpenAI
import os
from dotenv import load_dotenv
from json_example import prompt_example
import json
load_dotenv()

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  
)

def read_markdown(md_path, file_path):
    with open(os.path.join(md_path, file_path), 'r', encoding='utf-8') as file:
        return file.read()
    
def query_gpt(prompt, model="gpt-4o", max_tokens=500):
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
    
def process_markdown_with_gpt(markdown_content, questions, q_type):
    extracted_data = {}
    for question in questions:
        print(f"Processing: {question}")
        if q_type == 'gq':
            prompt = f"Based on the following academic paper content:\n\n{markdown_content}\n\n{question}"
        elif q_type == 'xy':
            formulas_example = """$$ E X B M S_{i,k}=\frac{B M S_{i,k}-N B M S_{i}}{N B P S_{i}}.$$"""
            prompt = f"""
            You are a statistics expert specializing in finance. Your task is to identify the variables X or Y used in the model and organize them in a structured JSON format.
            You will be provided with a markdown content and a question.
            
            **markdown_content**: \n{markdown_content}
            **question**: \n{question}
            **json_example**: \n{prompt_example.example['json_example']}
            ***
            You must focus on only MATH FORMULAS:
            
            Key Instruction for Focusing on MATH FORMULAS in Markdown
                You need to follow these steps:
                    - Focus only on content in mathematical format. These formulas are typically enclosed within $$ symbols, e.g., $$ FORMULA $$.
                    - Do not include any text, symbols, or variables (e.g., X, Y) that are not part of a properly formatted mathematical expression.
                    - Example of mathematical format in Markdown: {formulas_example}
                    - Identify and convert mathematical variables or terms into human-understandable phrases based on the context of the research paper.
                        - Use the research paper context to clarify abbreviations. For example:
                            - LMktCap → "Logarithm of Market Capitalization"
                            - IVol → "Idiosyncratic Volatility"
                        - Ensure that each term is accurately translated while retaining its original meaning and relevance within the paper’s context.
                        - Do not make assumptions without clear evidence from the paper. If the meaning is unclear, use original mathematical term
                        
                    - Ensure that each term is accurately translated while retaining its original meaning and relevance within the paper’s context.
            ***
            
            I need to extract unique equations with their independent (X) and dependent (Y) variables from research papers. Each equation should have:
                - A unique set of independent variables (X).
                - A unique dependent variable (Y).
                - No overlap or duplication between equations.
                - Clear labels like "Equation_1", "Equation_2", etc.

            Ensure that:
                - Each equation is unique and meaningful.
                - If any independent variables are reused, they must lead to a different dependent variable.
            
            """
        response = query_gpt(prompt)
        extracted_data[question] = response
    return extracted_data

def main():
    md_path = os.path.join(os.getcwd(), '../', '_static/md')
    contents = os.listdir(md_path)
    for markdown_file in contents:
        # markdown_file = "../../[AR] -2011 - Investor Trading and the Post-Earnings-Announcement Drift/[AR] -2011 - Investor Trading and the Post-Earnings-Announcement Drift.md"
        output_dir = f"../output_dir/{markdown_file}"
        os.makedirs(output_dir, exist_ok=True)
        markdown_content = read_markdown(md_path, markdown_file)

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
            "What are the sample characteristics such as time period and sample firms?"
        ]

        x_y_questions = [
            """
            - What are the key dependent variables analyzed (Y, e.g., abnormal returns, trading volume)?
            - What are the key independent variables (X) used for regression or subsets?
            """
        ]

        extracted_data = process_markdown_with_gpt(markdown_content, questions, 'gq')

        json_data = json.dumps(extracted_data, indent=2)
        output_file = os.path.join(output_dir, "extracted_gq.json")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(json_data)

        extracted_data = process_markdown_with_gpt(markdown_content, x_y_questions, 'xy')

        # json_data = json.dumps(extracted_data, indent=2)
        json_data = list(extracted_data.values())[0].replace('json', '').strip().strip("`").strip("'")
        output_file = os.path.join(output_dir, f"extracted_xy.json")
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(json_data, file)

        print(f"Extraction complete. Results saved to {output_file}")

if __name__ == "__main__":

    main()