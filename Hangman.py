#import base pre-installed packages
import subprocess
import sys
import random
import json

#install / update required packages
packages = ["wonderwords", "python-datamuse"]
print("Updating needed packages...")
def update_packages():
    python_exe = sys.executable
    try:
        subprocess.check_call([python_exe, "-m", "pip", "install", *packages], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during installation: {e}")

def _run_pip_upgrade():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip. Error: {e}")

#Run package manager
update_packages()
_run_pip_upgrade()

#apply newly installed package
from wonderwords import RandomWord
from datamuse import Datamuse

def generate_hints(random_word, ww, max_per_category=5):
    #Generate Random word with random word package
    hints = []
    api = Datamuse()
    if random_word in ww.filter(include_categories=["noun"]):
        hints.append("The word is a noun")
    elif random_word in ww.filter(include_categories=["verb"]):
        hints.append("The word is a verb")
    elif random_word in ww.filter(include_categories=["adjective"]):
        hints.append("The word is a adjective")

    root = random_word[:4] if len(random_word) > 4 else random_word

    def extract_clean_words(api_results):
        return [item['word'] for item in api_results if root not in item['word'].lower()]

    adjectives = extract_clean_words(api.words(rel_jjb=random_word, max=max_per_category))
    associations = extract_clean_words(api.words(rel_trg=random_word, max=max_per_category))
    rhymes = extract_clean_words(api.words(rel_rhy=random_word, max=max_per_category))

    if adjectives:
        hints.append(f"This word is often described as: {random.choice(adjectives)}")
    if associations:
        hints.append(f"This word is associated with: {random.choice(associations)}")
    if rhymes:
        hints.append(f"This word rhymes with: {random.choice(rhymes)}")

    return hints

points = 0
try:
    with open("HighScore.txt", "r", encoding="utf-8") as file:
        highscore = int(file.read().strip() or 0)
except (FileNotFoundError, ValueError):
    highscore = 0

shop_items = {
    "1": {
        "name": "Extra Hint",
        "price": 5,
        "description": "Reveals an additional word hint."
    },
    "2": {
        "name": "Free Letter",
        "price": 10,
        "description": "Automatically reveals one letter."
    },
    "3": {
        "name": "Double or Nothing",
        "price": 15,
        "description": "Doubles your round score if you win."
    }
}

def inventory_screen():

    print("\n========== INVENTORY ==========")

    for item, quantity in available_powerups.items():
        print(f"{item}: {quantity}")

    input("\nPress Enter to return.")


def shop():
    global points, available_powerups

    while True:
        print("\n========== SHOP ==========")
        print(f"Your Points: {points}")

        for number, item in shop_items.items():
            print(f"\n{number}. {item['name']}")
            print(f"Price: {item['price']} points")
            print(f"Description: {item['description']}")

        print("\nType exit to return to menu.")

        selected_item = input("\nPurchase: ").lower().strip()

        if selected_item == "exit":
            return

        if selected_item not in shop_items:
            print("Invalid selection.")
            continue

        item = shop_items[selected_item]
        item_name = item["name"]
        item_price = item["price"]

        if points < item_price:
            print("You don't have enough points!")
            continue

        points -= item_price

        available_powerups[item_name] += 1

        save_inventory(available_powerups)

        print(f"\nSuccessfully purchased {item_name}!")
        print(f"Remaining points: {points}")

def load_inventory():
    try:
        with open("Items.json", "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return {
            "Extra Hint": 0,
            "Free Letter": 0,
            "Double or Nothing": 0
        }

    except json.JSONDecodeError:
        print("Inventory file corrupted. Creating new inventory.")
        return {
            "Extra Hint": 0,
            "Free Letter": 0,
            "Double or Nothing": 0
        }

def save_inventory(inventory):
    with open("Items.json", "w") as file:
        json.dump(inventory, file, indent=4)

available_powerups = load_inventory()


#main game starts here
def main():
    round_points = 0
    double_points = False
    global points
    print("Welcome to Hangman")
    print("What difficulty would you like: Easy, Normal, Hard, Random, Custom")
    max_attempts = 0
    r_num = 0
    #Run Difficulty selection
    while True:
        mode = input().lower()
        if mode == "easy":
            max_attempts_temp = 7
            r_num_temp = random.randint(3, 5)
            max_attempts = max_attempts_temp
            r_num = r_num_temp
            break

        elif mode == "normal":
            max_attempts_temp = random.randint(5, 6)
            r_num_temp = random.randint(4, 6)
            max_attempts = max_attempts_temp
            r_num = r_num_temp
            break

        elif mode == "hard":
            max_attempts_temp = random.randint(3, 4)
            r_num_temp = random.randint(6, 10)
            max_attempts = max_attempts_temp
            r_num = r_num_temp
            break

        elif mode == "random":
            max_attempts_temp = random.randint(3, 7)
            r_num_temp = random.randint(3, 10)
            max_attempts = max_attempts_temp
            r_num = r_num_temp
            break

        elif mode == "custom":
            while True:
                print("Set the max attempts allowed in a round: 1-6")
                max_attempts_input = int(input())
                if max_attempts_input < 1 or max_attempts_input > 6:
                    print("Please enter a valid number in the range")
                    continue
                else:
                    max_attempts_temp = max_attempts_input
                    max_attempts = max_attempts_temp
                    break

            while True:
                print("Set the letter count for the generated word: Minimum of 2")
                r_num_input = int(input())
                if r_num_input < 2:
                    print("Please enter a valid number in the range")
                    continue
                else:
                    r_num_temp = r_num_input
                    r_num = r_num_temp
                    break
            break


        else:
            print("Please enter one of the options: easy, normal, hard, random, custom")
            continue

    guessed = []
    wrong_guesses = 0

    #Establish Hangman stages
    hangman = [
        """
         -----
         |   |
             |
             |
             |
        =========
        """,
        """
         -----
         |   |
         O   |
             |
             |
        =========
        """,
        """
         -----
         |   |
         O   |
         |   |
             |
        =========
        """,
        """
         -----
         |   |
         O   |
         |\\  |
             |
        =========
        """,
        """
         -----
         |   |
         O   |
        /|\\  |
             |
        =========
        """,
        """
         -----
         |   |
         O   |
        /|\\  |
          \\  |
        =========
        """,

        """
         -----
         |   |
         O   |
        /|\\  |
        / \\  |
        ========
        """,

        """
        -----
         |   |
        -^-  | 
         O   |
        /|\\  |
        / \\  |
       =========
        """
    ]

    w = RandomWord()
    selected_word = w.word(word_max_length=r_num, exclude_with_spaces=True)

    generated_hint = generate_hints(selected_word, w)
    for i, hint in enumerate(generated_hint, 1):
        hint = f"Hint: {hint}"

    if available_powerups["Free Letter"] > 0:

        use_item = input(
            "Use Free Letter? (y/n): "
        ).lower()

        if use_item == "y":

            available_letters = [
                letter for letter in set(selected_word)
                if letter not in guessed
            ]

            if available_letters:
                revealed_letter = random.choice(
                    available_letters
                )

                guessed.append(revealed_letter)

                available_powerups["Free Letter"] -= 1

                save_inventory(available_powerups)

                print(f"Free letter revealed: {revealed_letter}")

    if available_powerups["Extra Hint"] > 0:

        use_item = input(
            "Use Extra Hint? (y/n): "
        ).lower()

        if use_item == "y":

            if generated_hint:

                print("Extra Hint:")
                print(random.choice(generated_hint))

                available_powerups["Extra Hint"] -= 1

                save_inventory(available_powerups)

            else:
                print("No additional hints available.")

    if available_powerups["Double or Nothing"] > 0:

        use_item = input(
            "Use Double or Nothing? (y/n): "
        ).lower()

        if use_item == "y":
            double_points = True

            available_powerups["Double or Nothing"] -= 1

            save_inventory(available_powerups)

            print("Double or Nothing activated!")

    #Start main game loop
    while wrong_guesses < max_attempts:

        display = ""

        for letter in selected_word:
            if letter in guessed:
                display += letter + " "
            else:
                display += "_ "
        if wrong_guesses == (max_attempts - 1):
            print(hangman[6])
        elif wrong_guesses == max_attempts:
            print(hangman[-1])
        else:
            print(hangman[wrong_guesses])
        print(f"You have {points} points!")
        print(hint)
        print("Word:", display)

        if "_" not in display:
            print("Congratulations! You win!")
            print("The word was: ", selected_word)
            if double_points:
                print("You won double or nothing!")
                points = points * 2
                print(f"You have {points}!")

            break

        guess = input("Guess a letter: ").lower()

        if len(guess) != 1 or not guess.isalpha():
            print("Please enter one letter.")
            continue

        if guess in guessed:
            print("You already guessed this letter.")
            continue

        guessed.append(guess)

        if guess in selected_word:
            print("Correct guess!")
            points += 1
        else:
            wrong_guesses += 1
            print("Wrong guess!")
            print("(", wrong_guesses, "/", max_attempts, ")")
            if points > 0:
                points -= 1
    else:
        print(hangman[wrong_guesses])
        print("Game Over!")
        print("The word was: ", selected_word)
        if double_points:
            print("You lost everything!!!")
            print("You have 0 points.")
            points = 0
    user_choice = input("\nWould you like to try again? (y/n): ").lower().strip()
    if user_choice == "y":
        main()
    else:
        print("Updating HighScore.....")
        global highscore
        if points > highscore:
            highscore = points

            with open("HighScore.txt", "w", encoding="utf-8") as file:
                file.write(str(highscore))

            print("New High Score!")

        print("Good Game!")
        print("Returning to Main Menu.....")
        menu()
    return()


def menu():

    while True:

        print("\n========== MAIN MENU ==========")
        print("1. Play")
        print("2. Shop")
        print("3. Inventory")
        print("4. Scores")
        print("5. Exit")

        selection = input("\nSelect: ").lower().strip()

        if selection == "1" or selection == "play":
            main()

        elif selection == "2" or selection == "shop":
            shop()

        elif selection == "3" or selection == "inventory":
            inventory_screen()

        elif selection == "4" or selection == "scores":
            print(f"Highscore: {highscore}")

        elif selection == "5" or selection == "exit":
            print("Good Game!")
            exit()

        else:
            print("Invalid selection.")
menu()