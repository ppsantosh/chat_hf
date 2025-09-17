
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
# Use a lightweight model that works well for Q&A
MODEL_ID = "google/flan-t5-small"

# Force CPU
device = torch.device("cpu")

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to(device)

def answer_question(question: str) -> str:
    inputs = tokenizer(question, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

prompt = """
You are an AI expert.
when asked whether related question retrive the location for which whether has been asked.
respond only name of the location.

Example:
    What it the current whether of Bangalore
    Bangalore
    Tell me the whether of Boston?
    Boston
"""

prompt_city_name = """
You are an AI expert.
When asked check if it is a valid city name.

rules:
    if not valid city name response with INVALID  
    if valid city name respond with VALID
    
Example:
    Question: asdfghjkl
    INVALID
    Question: 12345
    INVALID
"""

query = ""
prompt_text = "Enter your question (or type 'exit' to quit): "


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    query = data.get('qn')
    if(query.strip() != "" and query.lower() != "exit"):            
        input_text = f"prompt:{prompt}\n\n question:{query}"    
        answer = answer_question(input_text)
        #print(F"answer:{answer}")
        input_text2 = f"prompt:{prompt_city_name}\n\n text:{answer}"    
        valid_response = answer_question(input_text2)
        #print(f"valid_response:{valid_response}")
        if valid_response != "INVALID":
            #print(f"Identified City:{answer}")
            try:
                whether = requests.get(f"https://wttr.in/{answer}?format=3").text
                return jsonify({"Whether of City ": answer, " V1 Whether ": whether})
                #print(f"Whether of {answer}: {whether}")
            except Exception as e:
                return jsonify({"Whether of City ": answer, " V1 Error ": e})
                #print(f"Could not retrieve whether for {answer}. Error: {e}")
        else:
            return jsonify({"Please enter a valid city name. ": "" ," and Error ": ""})
            #print("Please enter a valid city name.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
