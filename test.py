import http.client
import json

API_KEY = "OpenAI Key"

CSV_CONTENT = """Symbol,Company,YTD Return,6 Months Return,1 Week Return
AAPL,Apple Inc.,x,x,x
GOOG,Alphabet Inc.,x,x,x
AMZN,Amazon.com Inc.,x,x,x
TSLA,Tesla Inc.,x,x,x
"""

def complete_csv_with_openai(csv_text):
    conn = http.client.HTTPSConnection("api.openai.com")
    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {API_KEY}"
    }

    prompt_text = (
        "This is a CSV file containing stock information. "
        "Wherever you find 'x', replace it with realistic and appropriate example data (use % for returns). "
        "Return the completed CSV only, without explanations.\n\n"
        f"{csv_text}"
    )

    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.2
    }

    json_data = json.dumps(data)

    conn.request("POST", "/v1/chat/completions", body=json_data, headers=headers)
    res = conn.getresponse()
    response_text = res.read().decode("utf-8")

    if res.status == 200:
        response_json = json.loads(response_text)
        completed_csv = response_json['choices'][0]['message']['content']
        print("\nCompleted CSV:\n")
        print(completed_csv)
    else:
        print(f"Request failed with status {res.status}: {response_text}")

if __name__ == "__main__":
    complete_csv_with_openai(CSV_CONTENT)
