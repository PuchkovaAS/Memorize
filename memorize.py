from enum import Enum
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FlashcardsOrm(Base):
    __tablename__ = 'flashcard'

    id = Column(Integer, primary_key=True)
    answer = Column(String)
    question = Column(String)
    box_number = Column(Integer)


class Menu(Enum):
    EXIT = 0
    START = 1
    ADD_FLASHCARD = 2
    PRACTICE = 3


class Flashcards:
    def __init__(self):
        self.current_card = None
        self.engine = create_engine('sqlite:///flashcard.db', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # self.update_collumn()

    def update_collumn(self):
        self.engine.connect().execute('UPDATE flashcard SET box_number = 1;')
        self.session.commit()

    def add_collumn(self):
        self.engine.connect().execute('ALTER TABLE flashcard ADD CONSTRAINT Integer DEFAULT 1 FOR box_number')
        self.session.commit()

    def add_new_cards(self, question, answer):
        new_data = FlashcardsOrm(question=question, answer=answer, box_number=1)
        self.session.add(new_data)
        self.session.commit()

    def get_current_card(self):
        return self.current_card.question, self.current_card.answer

    def get_cards(self, cur_session):
        for flash_card in self.session.query(FlashcardsOrm).filter(FlashcardsOrm.box_number <= cur_session):
            self.current_card = flash_card
            yield flash_card.question, flash_card.answer

    def update_box(self, n):
        if 4 >= (self.current_card.box_number + n) >= 1:
            self.current_card.box_number += n
            self.session.commit()
        if self.current_card.box_number == 4:
            self.delete_current_card()

    def update_current_card(self, question, answer):
        self.current_card.question = question
        self.current_card.answer = answer
        self.session.commit()

    def delete_current_card(self):
        self.session.delete(self.current_card)
        self.session.commit()

    def not_exist(self):
        return self.session.query(FlashcardsOrm).count() == 0


class MemoriSystem:

    def __init__(self):
        self.curr_section = 1
        self.flashcards = Flashcards()
        self.curr_menu = Menu.START

    def menu(self):
        while self.curr_menu != Menu.EXIT:
            if self.curr_menu == Menu.START:
                self.start_menu()
            elif self.curr_menu == Menu.ADD_FLASHCARD:
                self.add_flashcards_menu()
            elif self.curr_menu == Menu.PRACTICE:
                self.practice_menu()

        print("\nBye!")

    def add_flashcards_menu(self):
        print("""\n1. Add a new flashcard
2. Exit""")
        selected_menu = input()
        if selected_menu == '1':
            self.add_flashcards()
        elif selected_menu == '2':
            self.curr_menu = Menu.START
        else:
            print(f"{selected_menu} is not an option")

    def edit_menu(self):
        cur_question, cur_answer = self.flashcards.get_current_card()
        print(f"""\ncurrent question: {cur_question}
please write a new question:""")
        question = input()
        if question == "":
            question = cur_question
        print(f"""\ncurrent answer: {cur_answer}
please write a new answer:""")
        answer = input()
        if answer == "":
            answer = cur_answer
        self.flashcards.update_current_card(question=question, answer=answer)

    def update_menu(self):
        print("""press "d" to delete the flashcard:
press "e" to edit the flashcard:""")
        answ = input()
        if answ == 'd':
            self.flashcards.delete_current_card()
        elif answ == 'e':
            self.edit_menu()
        else:
            print(f"{answ} is not an option")

    def add_flashcards(self):
        question = ""
        while question == "":
            print("\nQuestion:")
            question = input()
        answer = ""
        while answer == "":
            print("Answer:")
            answer = input()
        self.flashcards.add_new_cards(question=question, answer=answer)

    def check_answer(self):
        while 1:
            print("""press "y" if your answer is correct:
press "n" if your answer is wrong:""")
            answ = input()
            if answ == 'y':
                self.flashcards.update_box(n=1)
                break
            elif answ == 'n':
                self.flashcards.update_box(n=-1)
                break
            else:
                print(f"{answ} is not an option")

    def practice_menu(self):
        if self.flashcards.not_exist():
            print("\nThere is no flashcard to practice!\n")
            self.curr_menu = Menu.START
            return

        for question, answer in self.flashcards.get_cards(cur_session=self.curr_section):
            print(f"""\nQuestion: {question}:""")
            while 1:
                print("""press "y" to see the answer:
press "n" to skip:
press "u" to update:""")
                answ = input()
                if answ == 'y':
                    print(f"Answer: {answer}")
                    self.check_answer()
                    break
                elif answ == 'u':
                    self.update_menu()
                    break
                elif answ == 'n':
                    self.curr_menu = Menu.START
                    self.check_answer()
                    break
                else:
                    print(f"{answ} is not an option")
        self.curr_menu = Menu.START
        self.curr_section += 1

    def start_menu(self):
        print("""\n1. Add flashcards
2. Practice flashcards
3. Exit""")
        selected_menu = input()
        if selected_menu == '1':
            self.curr_menu = Menu.ADD_FLASHCARD
        elif selected_menu == '2':
            self.curr_menu = Menu.PRACTICE
        elif selected_menu == '3':
            self.curr_menu = Menu.EXIT
        else:
            print(f"{selected_menu} is not an option")


if __name__ == "__main__":
    test = MemoriSystem()
    test.menu()
    # a = test.numbers_range(10)
# print(a.__next__())
# print(a.__next__())


# Base.metadata.create_all(engine) # создает базу


# Insert
# new_data = FlashcardsOrm(question="What is the capital city of Hungary?", answer="Budapest")
# session.add(new_data)
# session.commit()


# Select
# for post in session.query(FlashcardsOrm):
#     print(post)
