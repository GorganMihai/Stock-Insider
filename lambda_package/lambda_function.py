import boto3
import http.client
import json

S3_BUCKET_NAME = "csv-stock-bucket-2025"
S3_OBJECT_KEY = "watchlist.csv"
OPENAI_API_KEY = "OpenAI API key"

s3_client = boto3.client('s3')


def ask_openai_to_complete_csv(csv_text):
    conn = http.client.HTTPSConnection("api.openai.com")
    headers = {
        'Content-Type': "application/json",
        'Authorization': f"Bearer {OPENAI_API_KEY}"
    }

    prompt_text = (
    "You are a data processing assistant specialized in stock market data, you find the data on yahoo finance site.\n"
    "You receive a CSV file with the following columns:\n"
    "- Symbol: stock ticker symbol of the company (e.g. AAPL)\n"
    "- Company: official company name corresponding to the ticker symbol\n"
    "- YTD Return: Year-To-Date stock return percentage (%), based on real-world market performance\n"
    "- 6 Months Return: stock return percentage (%) over the last 6 months\n"
    "- 1 Week Return: stock return percentage (%) over the last 1 week\n\n"
    "Missing values are marked as 'x'. Replace each 'x' with realistic numeric percentages reflecting actual market conditions as of 2025.\n"
    "Use both positive and negative values where appropriate.\n"
    "Always include the '%' symbol after each number.\n"
    "Ensure:\n"
    "- The Company name exactly matches the Symbol.\n"
    "- All data is plausible and consistent with current 2025 stock market trends.\n"
    "- Do NOT generate extreme or unrealistic returns.\n"
    "- Do NOT add any explanation, code formatting, or extra text.\n"
    "- Return ONLY the completed CSV file, starting directly from the header row.\n\n"
    + csv_text
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

    if res.status != 200:
        raise Exception(f"OpenAI error {res.status}: {response_text}")

    response_json = json.loads(response_text)
    completed_csv = response_json['choices'][0]['message']['content']
    return completed_csv


def lambda_handler(event, context):
    try:
        # 1. Download CSV from S3
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_KEY)
        csv_content = response['Body'].read().decode('utf-8')

        # 2. Check for missing values ('x')
        if 'x' not in csv_content:
            print("No missing values detected. Lambda execution stopped.")
            return {
                'statusCode': 200,
                'body': 'CSV is already complete. No action taken.'
            }

        # 3. Send CSV to OpenAI for completion
        completed_csv = ask_openai_to_complete_csv(csv_content)

        # 4. Upload the completed CSV back to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=S3_OBJECT_KEY,
            Body=completed_csv.encode('utf-8')
        )

        print("CSV completed and uploaded to S3.")

        return {
            'statusCode': 200,
            'body': 'CSV processed and updated by OpenAI.'
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f'Error: {e}'
        }
