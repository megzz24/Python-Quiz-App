import requests
import random
import html


def get_categories():
    url = "https://opentdb.com/api_category.php"
    response = requests.get(url)
    data = response.json()
    return data["trivia_categories"]


def get_token():
    url = "https://opentdb.com/api_token.php?command=request"
    response = requests.get(url)
    return response.json().get("token")


def reset_token(token):
    url = f"https://opentdb.com/api_token.php?command=reset&token={token}"
    requests.get(url)


def fetch_questions(
    amount=5, category=None, difficulty=None, question_type="multiple", token=None
):
    url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "category": category,
        "difficulty": difficulty,
        "type": question_type,
        "token": token,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["response_code"] == 4:
        print("All questions seen. Resetting token...")
        reset_token(token)
        return fetch_questions(
            amount=amount,
            category=category,
            difficulty=difficulty,
            question_type=question_type,
            token=token,
        )
    elif data["response_code"] == 0:
        return data["results"]
    else:
        print("Error fetching questions!")
        return []


def run_quiz():
    print("Welcome to the Quiz App!")

    token = get_token()

    categories = get_categories()
    print(categories)
    print("\nCategories:")
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category['name']}")

    try:
        choice1 = int(input("\nEnter a category number (or 0 for random): "))
        if choice1 == 0:
            category_id = None
        elif 1 <= choice1 <= len(categories):
            category_id = categories[choice1 - 1]["id"]
        else:
            print("Invalid choice. Using random category.")
            category_id = None
    except ValueError:
        category_id = None

    choice2 = input(
        "Choose difficulty. Enter 'e' for easy, 'm' for medium,'h' for hard: "
    )
    if choice2 == "e":
        difficulty = "easy"
    elif choice2 == "m":
        difficulty = "medium"
    elif choice2 == "h":
        difficulty = "hard"
    else:
        print("Invalid choice. Using random difficulty.")
        difficulty = None

    score = 0
    questions = fetch_questions(
        category=category_id, difficulty=difficulty, token=token
    )

    if not questions:
        print(
            "No new questions available. Try resetting the token or choosing another category."
        )
        return

    for i, q in enumerate(questions, 1):
        question = html.unescape(q["question"])
        correct = html.unescape(q["correct_answer"])
        incorrect = [html.unescape(answer) for answer in q["incorrect_answers"]]
        options = incorrect + [correct]
        random.shuffle(options)

        print(f"\nQ{i}: {question}")
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option}")

        while True:
            try:
                answer = int(input("Your answer (1-4): "))
                if 1 <= answer <= len(options):
                    if options[answer - 1] == correct:
                        print("Correct!")
                        score += 1
                    else:
                        print(f"Wrong! The correct answer was: {correct}")
                    break
                else:
                    print(f"Please enter a number between 1 and {len(options)}.")
            except ValueError:
                print("Please enter a valid number.")

    print(f"\n Quiz Finished! Your Score: {score}/{len(questions)}")


if __name__ == "__main__":
    try:
        while True:
            run_quiz()
            again = input("\nDo you want to play again? (y/n): ").strip().lower()
            if again != "y":
                print("Thanks for playing!")
                break
    except KeyboardInterrupt:
        print("\nThanks for playing!")
