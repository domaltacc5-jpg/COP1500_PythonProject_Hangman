#import base pre-installed packages
import subprocess
import sys
import random

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
with open("HighScore.txt", "r") as file:
    highscore = int(file.readline().strip())




#main game starts here
def main():
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
            print("Please enter one of the options: easy, normal, hard")
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
    return()

#script manager
if __name__ == "__main__":
    while True:
        main()
        user_choice = input("\nWould you like to try again? (y/n): ").lower().strip()

        if user_choice != "y":
            print("Updating HighScore.....")
            with open ("HighScore.txt", "r+", encoding="utf8") as file:
                temp_highscore = int(file.readline().strip())
                if temp_highscore < 0:
                    temp_highscore = 0
                if temp_highscore < points:
                    with open("HighScore.txt", "w", encoding="utf8") as f:
                        pass
                    file.write(str(points))
            if points > highscore:
                print("New High Score!")
            print("Good Game!")
            break