
# 심신통합 헬스케어 퀴즈 게임
# 데이터 저장 파일: state.json

import json
from pathlib import Path


# 프로젝트 폴더 안에 state.json 파일을 생성합니다.
DATA_FILE = Path(__file__).with_name("state.json")


class Quiz:
    """퀴즈 한 문제의 정보를 관리하는 클래스"""

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def to_dict(self):
        """퀴즈 정보를 저장할 수 있는 딕셔너리로 변환합니다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }


class QuizGame:
    """퀴즈 게임의 기능을 관리하는 클래스"""

    def __init__(self):
        self.quizzes = self.get_default_quizzes()

        # 최고 점수 정보
        self.high_score = 0
        self.high_score_correct = 0
        self.high_score_total = 0

        # 저장된 데이터가 있으면 불러옵니다.
        self.load_state()

    def get_default_quizzes(self):
        """처음 실행할 때 사용할 기본 퀴즈 5개를 만듭니다."""

        return [
            Quiz(
                "심신통합 헬스케어에서 가장 먼저 실천할 것은 무엇일까요?",
                [
                    "다른 사람과 비교하기",
                    "내 몸과 마음 상태 알아차리기",
                    "무조건 운동량 늘리기",
                    "불편한 감정 무시하기"
                ],
                2
            ),
            Quiz(
                "스트레스를 느낄 때 도움이 되는 행동은 무엇일까요?",
                [
                    "자신의 호흡과 몸 상태를 살펴보기",
                    "감정을 무조건 참기",
                    "휴식 없이 계속 일하기",
                    "주변 사람에게 화내기"
                ],
                1
            ),
            Quiz(
                "일상적인 신체활동을 할 때 바람직한 태도는 무엇일까요?",
                [
                    "통증이 있어도 계속하기",
                    "다른 사람의 운동량 따라 하기",
                    "자신의 체력에 맞게 무리하지 않기",
                    "준비 없이 갑자기 강하게 운동하기"
                ],
                3
            ),
            Quiz(
                "건강한 수면 습관을 위한 방법으로 적절한 것은 무엇일까요?",
                [
                    "매일 수면 시간을 크게 바꾸기",
                    "잠들기 직전 카페인 섭취하기",
                    "잠이 오지 않아도 억지로 버티기",
                    "일정한 수면 습관 유지하기"
                ],
                4
            ),
            Quiz(
                "몸과 마음의 불편함이 지속되어 일상생활에 지장을 준다면 어떻게 해야 할까요?",
                [
                    "무조건 참기",
                    "필요한 경우 전문가의 도움받기",
                    "증상을 다른 사람에게 숨기기",
                    "휴식과 상담을 모두 피하기"
                ],
                2
            )
        ]

    def load_state(self):
        """state.json 파일에서 퀴즈와 최고 점수를 불러옵니다."""

        if not DATA_FILE.exists():
            print("\n저장된 데이터가 없습니다. 기본 퀴즈로 시작합니다.")
            self.save_state()
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            loaded_quizzes = []

            for item in data["quizzes"]:
                question = item["question"]
                choices = item["choices"]
                answer = item["answer"]

                if (
                    isinstance(question, str)
                    and question.strip()
                    and isinstance(choices, list)
                    and len(choices) == 4
                    and all(
                        isinstance(choice, str) and choice.strip()
                        for choice in choices
                    )
                    and isinstance(answer, int)
                    and not isinstance(answer, bool)
                    and 1 <= answer <= 4
                ):
                    loaded_quizzes.append(
                        Quiz(question, choices, answer)
                    )

            if not loaded_quizzes:
                raise ValueError("저장된 퀴즈 데이터가 올바르지 않습니다.")

            self.quizzes = loaded_quizzes

            self.high_score = max(0, int(data.get("high_score", 0)))
            self.high_score_correct = max(
                0, int(data.get("high_score_correct", 0))
            )
            self.high_score_total = max(
                0, int(data.get("high_score_total", 0))
            )

            print("저장된 퀴즈 데이터를 불러왔습니다.")

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ):
            print("\n저장 파일이 없거나 손상되었습니다.")
            print("기본 퀴즈 데이터로 다시 시작합니다.")

            self.quizzes = self.get_default_quizzes()
            self.high_score = 0
            self.high_score_correct = 0
            self.high_score_total = 0

            self.save_state()

    def save_state(self):
        """현재 퀴즈와 최고 점수를 state.json에 저장합니다."""

        data = {
            "quizzes": [
                quiz.to_dict() for quiz in self.quizzes
            ],
            "high_score": self.high_score,
            "high_score_correct": self.high_score_correct,
            "high_score_total": self.high_score_total
        }

        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            return True

        except OSError as error:
            print(f"\n데이터 저장에 실패했습니다: {error}")
            return False

    def show_menu(self):
        """메뉴를 화면에 표시합니다."""

        print("\n" + "=" * 40)
        print("       심신통합 헬스케어 퀴즈")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 최고 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def get_nonempty_input(self, message):
        """빈 입력을 허용하지 않고 다시 입력받습니다."""

        while True:
            value = input(message).strip()

            if value:
                return value

            print("내용을 비워둘 수 없습니다. 다시 입력해 주세요.")

    def get_number_input(self, message, minimum, maximum):
        """정해진 범위 안의 숫자를 입력받습니다."""

        while True:
            value = input(message).strip()

            if not value:
                print("숫자를 입력해 주세요.")
                continue

            try:
                number = int(value)

                if minimum <= number <= maximum:
                    return number

                print(
                    f"{minimum}~{maximum} 사이의 번호를 입력하세요."
                )

            except ValueError:
                print("숫자로 입력해 주세요.")

    def play_quiz(self):
        """등록된 퀴즈를 순서대로 출제합니다."""

        print("\n[심신통합 헬스케어 퀴즈 시작]")

        score = 0
        total = len(self.quizzes)

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n문제 {number}. {quiz.question}")

            for i, choice in enumerate(quiz.choices, start=1):
                print(f"{i}. {choice}")

            answer = self.get_number_input(
                "정답 번호를 입력하세요(1~4): ",
                1,
                4
            )

            if answer == quiz.answer:
                print("정답입니다!")
                score += 1
            else:
                print(f"아쉽습니다. 정답은 {quiz.answer}번입니다.")

        percentage = score * 100 // total

        print("\n===== 퀴즈 결과 =====")
        print(f"총 문제 수: {total}")
        print(f"맞힌 문제 수: {score}")
        print(f"점수: {percentage}점")

        if percentage > self.high_score:
            self.high_score = percentage
            self.high_score_correct = score
            self.high_score_total = total

            print("\n축하합니다! 최고 점수를 갱신했습니다.")

        self.save_state()

    def add_quiz(self):
        """사용자가 새로운 퀴즈를 직접 추가합니다."""

        print("\n[새로운 퀴즈 추가]")

        question = self.get_nonempty_input(
            "문제를 입력하세요: "
        )

        choices = []

        for i in range(1, 5):
            choice = self.get_nonempty_input(
                f"{i}번 선택지를 입력하세요: "
            )
            choices.append(choice)

        answer = self.get_number_input(
            "정답 번호를 입력하세요(1~4): ",
            1,
            4
        )

        new_quiz = Quiz(question, choices, answer)
        self.quizzes.append(new_quiz)

        print("\n새로운 퀴즈가 추가되었습니다!")
        print(f"현재 등록된 퀴즈 수: {len(self.quizzes)}개")

        self.save_state()

    def show_quizzes(self):
        """등록된 퀴즈 목록을 보여줍니다."""

        print("\n[심신통합 헬스케어 퀴즈 목록]")

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n문제 {number}. {quiz.question}")

            for i, choice in enumerate(quiz.choices, start=1):
                print(f"  {i}. {choice}")

    def show_high_score(self):
        """저장된 최고 점수를 보여줍니다."""

        print("\n===== 최고 점수 =====")

        if self.high_score_total == 0:
            print("아직 기록된 점수가 없습니다.")
        else:
            print(f"최고 점수: {self.high_score}점")
            print(
                f"정답 수: {self.high_score_correct}"
                f"/{self.high_score_total}문제"
            )

    def run(self):
        """프로그램을 실행하고 메뉴를 반복합니다."""

        print("\n심신통합 헬스케어 퀴즈 게임에 오신 것을 환영합니다!")

        try:
            while True:
                self.show_menu()

                choice = input(
                    "메뉴 번호를 선택하세요: "
                ).strip()

                if choice == "1":
                    self.play_quiz()

                elif choice == "2":
                    self.add_quiz()

                elif choice == "3":
                    self.show_quizzes()

                elif choice == "4":
                    self.show_high_score()

                elif choice == "5":
                    print("\n심신통합 헬스케어 퀴즈를 종료합니다.")
                    break

                else:
                    print(
                        "\n잘못된 입력입니다. "
                        "1~5 사이의 번호를 입력하세요."
                    )

        except (KeyboardInterrupt, EOFError):
            print("\n\n입력이 중단되었습니다.")
            print("프로그램을 안전하게 종료합니다.")

        finally:
            self.save_state()
            print("데이터 저장을 확인했습니다.")


if __name__ == "__main__":
    game = QuizGame()
    game.run()
