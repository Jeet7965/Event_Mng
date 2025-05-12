
import openai
from django.conf import settings
openai.api_key = settings.OPENAI_API_KEY
def analyze_sentiment(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Analyze this feedback and classify its sentiment as Positive, Negative, or Neutral:\n\n{text}"
        }],
        max_tokens=10
    )
    sentiment = response.choices[0].message.content.strip()
    return sentiment