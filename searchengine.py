import openai
import requests

api_key = 'KEY'

openai.api_key = api_key


def fetch_school_data():
    url = 'https://sapient-api.kupyn.dev/schools'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


def chatgpt_search(query, school_data):
    prompt = f"Search for: {query}\nSchool Data: {school_data}\n"

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=50,
    )

    return response.choices[0].text.strip()


if __name__ == "__main__":
    school_data = fetch_school_data()
    if school_data is None:
        print("Failed to fetch school data. Check your Flask app URL.")
    else:
        print("School Data Fetched Successfully.")

    while True:
        query = input("Enter your search query (or 'exit' to quit): ")

        if query.lower() == 'exit':
            break

        result = chatgpt_search(query, school_data)
        print("Search Result:")
        print(result)
