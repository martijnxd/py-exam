#####
# run with -h to see all arguments
# run with -q/--quesion 10 to start with question 10
# run with -c/--count 20 to do 20 questions
# run with -r/--random to pick random questions
# run without args to dislay the questions from input file
# to scrape the exam html pages:
# set the html_source_dir with the downloaded html files 
# run with -s --scrape to scrape the exam html files and output the data to the output json
####

## user vars

# source dir with the downloaded html files
html_source_dir = "./aws-sysops-exam/"
# input json for the quiz
input_file = "./aws-sysops-exam.json"
# output json for the scraped data.
output_file = "./aws-sysops-exam-out.json"
# url = "https://www.examtopics.com/exams/amazon/aws-sysops/view/"
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

## end vars


import random
import itertools
import argparse
from PIL import Image
import json
import pandas as pd
import os
import requests
import textwrap
from bs4 import BeautifulSoup


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def fmtstring(long_string):
    wrapper = textwrap.TextWrapper()
    wrapper.width = 100
    return wrapper.fill(long_string)


def print_question(data, number):
    cls()
    q = data["questions"][number - 1]
    ta = ""
    img = ""
    if q["question_image"] != "NOIMAGE":
        img = Image.open(html_source_dir + q["question_image"].replace("./", ""))
        img.show()
    print(
        Blue
        + "Question {}".format(number)
        + ": "
        + fmtstring(q["question"])
        + "\n"
        + White
    )
    for item in q["options"]:
        print(item["item_letter"] + " " + item["item"])
    input("Press Enter to show the answer...")
    if q["answers"] != None:
        print(Red + "\nAnswer on site: ")
        for answer in q["answers"]:
            ta = ta + answer
        print(Red + ta + White)
    if q["answer_description"] != "":
        print("Description: " + fmtstring(q["answer_description"]))
    if q["answer_disc_count"] != None:
        print("\nNumber of comments: " + q["answer_disc_count"])
    print("Check discussion at: " + q["answer_disc"] + "\n\n")
    input("Press Enter to continue...")
    cls()


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--scrape", action="store_true", help="scrape the html files")
parser.add_argument("-c", "--count", type=int, default=0, help="amount of questions")
parser.add_argument("-r", "--random", action="store_true", help="show random")
parser.add_argument(
    "-q", "--question", type=int, default=0, help="question number to start with"
)

args = parser.parse_args()
White = "\033[0m"
Red = "\033[31m"
Blue = "\u001b[36m"
data = {}
# page = requests.get(url, headers=headers)

# start quiz with input file
if not args.scrape:
    with open(input_file, "r") as input_file:
        data = json.load(input_file)
    if args.count > 0:
        amount = args.count
    else:
        amount = len(data["questions"])
    if args.random:
        for _ in itertools.repeat(None, amount):
            print_question(data, random.randint(1, len(data["questions"])))
    elif args.question > 0:
        q = args.question
        if args.question + amount > len(data["questions"]):
            amount = len(data["questions"]) - args.question
        for _ in itertools.repeat(None, amount):
            print_question(data, q)
            q = q + 1
    else:
        q = 1
        for _ in itertools.repeat(None, amount):
            print_question(data, q)
            q = q + 1
# start scraping html
else:
    i = 0
    data["questions"] = []
    for filename in os.listdir(html_source_dir):
        if filename.endswith(".html"):
            fname = os.path.join(html_source_dir, filename)
            with open(fname, "r") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                questions = soup.find_all(class_="card exam-question-card")
                for question in questions:
                    i = i + 1
                    options = []
                    answers = []
                    for answer in question.find_all(
                        "li", class_="multi-choice-item correct-hidden"
                    ):
                        answers.append(
                            answer.find(
                                "span", class_="multi-choice-letter"
                            ).text.strip()
                        )
                    answer_description = question.find(class_="answer-description")
                    answer_disc = question.find(
                        "a",
                        class_="btn btn-secondary question-discussion-button d-print-none",
                    )
                    if question.find(class_="badge badge-pill badge-light") != None:
                        answer_disc_count = question.find(
                            class_="badge badge-pill badge-light"
                        ).text
                    choices = question.find_all(
                        "li", "span", class_="multi-choice-item"
                    )
                    question_text = question.find("p", class_="card-text")
                    if question.find("img", class_="in-exam-image") != None:
                        question_image = question.find("img", class_="in-exam-image")[
                            "src"
                        ]
                    else:
                        question_image = "NOIMAGE"
                    for choice in choices:
                        letter = choice.span.text
                        item = (choice.text).strip(letter)
                        options.append(
                            {
                                "item_letter": letter.strip(),
                                "item": (choice.text).strip(letter),
                            }
                        )
                    data["questions"].append(
                        {
                            "nr": i,
                            "question": question_text.text.strip(),
                            "question_image": question_image,
                            "options": options,
                            "answers": answers,
                            "answer_description": answer_description.text.strip(),
                            "answer_disc": answer_disc["href"],
                            "answer_disc_count": answer_disc_count,
                        }
                    )
    # write to file
    with open(output_file, "w") as output_file:
        json.dump(data, output_file)
