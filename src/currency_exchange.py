import os
import json
import boto3
import urllib.request

def format_currency_data(currency, rate):
    return (
        f"Currency Exchange Rate Update for {currency}:\n"
        f"Exchange Rate: {rate}\n"
    )

def lambda_handler(event, context):
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
    if not sns_topic_arn:
        print("SNS_TOPIC_ARN environment variable is not set.")
        return {
            "statusCode": 500,
            "body": json.dumps("SNS_TOPIC_ARN is not set or invalid.")
        }

    sns_client = boto3.client("sns")
    currencies = ["PHP", "CAD", "SGD"]
    base_currency = "USD"
    api_url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps("Error fetching exchange rates")
        }

    messages = []
    for currency in currencies:
        rate = rates.get(currency, "Unknown")
        message = format_currency_data(currency, rate)
        messages.append(message)

    for message in messages:
        try:
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=message,
                Subject="Currency Exchange Rate Update"
            )
        except Exception as e:
            print(f"Error publishing message to SNS: {e}")

    return {
        "statusCode": 200,
        "body": json.dumps("Data processed and sent to SNS")
    }

