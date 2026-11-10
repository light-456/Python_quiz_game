
# 심신통합 헬스케어 퀴즈 게임
# 데이터 저장 파일: state.json

import json
import random
import shutil
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).with_name("state.json")
# 손상된 저장 파일을 덮어쓰기 전에 보관해 두는 백업 파일
BACKUP_FILE = Path(__file__).with_name("state.json.bak")


class Quiz:
    """퀴즈 한 문제의 정보를 관리하는 클래스"""

    def __init__(self, question, choices, answer, explanation=""):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.explanation = explanation

    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "explanation": self.explanation
        }


class QuizGame:
    """퀴즈 게임의 기능을 관리하는 클래스"""

    def __init__(self):
        self.quizzes = self.get_default_quizzes()
        self.high_score = 0
        self.high_score_correct = 0
        self.high_score_total = 0
        self.score_history = []
        self.load_state()

    def get_default_quizzes(self):
        """기본 퀴즈 5개와 해설을 준비합니다."""

        return [
            Quiz(
                "심신통합 헬스케어에서 가장 먼저 실천할 것은 무엇일까요?",
                [
                    "다른 사람과 비교하기",
                    "내 몸과 마음 상태 알아차리기",
                    "무조건 운동량 늘리기",
                    "불편한 감정 무시하기"
                ],
                2,
                "자신의 현재 상태를 알아차려야 필요한 휴식과 활동을 적절하게 선택할 수 있습니다."
            ),
            Quiz(
                "스트레스를 느낄 때 도움이 되는 행동은 무엇일까요?",
                [
                    "자신의 호흡과 몸 상태를 살펴보기",
                    "감정을 무조건 참기",
                    "휴식 없이 계속 일하기",
                    "주변 사람에게 화내기"
                ],
                1,
                "호흡과 몸의 변화를 살펴보면 스트레스 상태를 알아차리고 자신에게 필요한 대응을 선택하는 데 도움이 됩니다."
            ),
            Quiz(
                "일상적인 신체활동을 할 때 바람직한 태도는 무엇일까요?",
                [
                    "통증이 있어도 계속하기",
                    "다른 사람의 운동량 따라 하기",
                    "자신의 체력에 맞게 무리하지 않기",
                    "준비 없이 갑자기 강하게 운동하기"
                ],
                3,
                "신체활동은 다른 사람과 비교하기보다 자신의 체력과 컨디션에 맞춰 안전하게 실천하는 것이 중요합니다."
            ),
            Quiz(
                "건강한 수면 습관을 위한 방법으로 적절한 것은 무엇일까요?",
                [
                    "매일 수면 시간을 크게 바꾸기",
                    "잠들기 직전 카페인 섭취하기",
                    "잠이 오지 않아도 억지로 버티기",
                    "일정한 수면 습관 유지하기"
                ],
                4,
                "일정한 시간에 자고 일어나는 습관은 규칙적인 수면 리듬을 만드는 데 도움이 됩니다."
            ),
            Quiz(
                "몸과 마음의 불편함이 지속되어 일상생활에 지장을 준다면 어떻게 해야 할까요?",
                [
                    "무조건 참기",
                    "필요한 경우 전문가의 도움받기",
                    "증상을 다른 사람에게 숨기기",
                    "휴식과 상담을 모두 피하기"
                ],
                2,
                "불편함이 지속되거나 일상생활에 영향을 준다면 혼자 참기보다 적절한 전문가의 도움을 받는 것이 좋습니다."
            )
        ]

    def load_state(self):
        """저장된 퀴즈와 최고 점수를 불러옵니다."""

        if not DATA_FILE.exists():
            print("\n저장된 데이터가 없습니다. 기본 퀴즈로 시작합니다.")
            self.save_state()
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("저장 데이터 형식이 올바르지 않습니다.")

            saved_quizzes = data.get("quizzes")

            if not isinstance(saved_quizzes, list):
                raise ValueError("퀴즈 목록 형식이 올바르지 않습니다.")

            default_explanations = {
                quiz.question: quiz.explanation
                for quiz in self.get_default_quizzes()
            }

            loaded_quizzes = []

            for item in saved_quizzes:
                if not isinstance(item, dict):
                    continue

                question = item.get("question")
                choices = item.get("choices")
                answer = item.get("answer")
                explanation = item.get("explanation", "")

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
                    and isinstance(explanation, str)
                ):
                    if not explanation.strip():
                        explanation = default_explanations.get(
                            question,
                            "이 문제의 핵심은 정답 선택지에 담긴 실천 방법을 일상에서 자신의 상태와 상황에 맞게 적용하는 것입니다."
                        )

                    loaded_quizzes.append(
                        Quiz(question, choices, answer, explanation)
                    )

            # 저장된 퀴즈가 있었는데 하나도 올바르지 않으면 손상된 것으로 봅니다.
            # (사용자가 모든 퀴즈를 삭제한 빈 목록은 정상 상태입니다.)
            if saved_quizzes and not loaded_quizzes:
                raise ValueError("저장된 퀴즈 데이터가 올바르지 않습니다.")

            self.quizzes = loaded_quizzes

            self.high_score = max(0, int(data.get("high_score", 0)))
            self.high_score_correct = max(
                0, int(data.get("high_score_correct", 0))
            )
            self.high_score_total = max(
                0, int(data.get("high_score_total", 0))
            )

            loaded_history = data.get("score_history", [])
            if not isinstance(loaded_history, list):
                loaded_history = []

            # 딕셔너리 형태의 기록만 사용합니다.
            self.score_history = [
                record for record in loaded_history
                if isinstance(record, dict)
            ]

            print("저장된 퀴즈 데이터를 불러왔습니다.")

            # 기존 데이터에 없던 해설도 저장 파일에 반영합니다.
            self.save_state()

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ):
            print("\n저장 파일이 손상되었거나 올바르지 않습니다.")
            self.backup_broken_file()
            print("기본 퀴즈 데이터로 다시 시작합니다.")

            self.quizzes = self.get_default_quizzes()
            self.high_score = 0
            self.high_score_correct = 0
            self.high_score_total = 0
            self.score_history = []

            self.save_state()

    def backup_broken_file(self):
        """손상된 state.json을 state.json.bak으로 복사해 둡니다."""

        try:
            shutil.copyfile(DATA_FILE, BACKUP_FILE)
            print(f"기존 파일은 {BACKUP_FILE.name}에 백업했습니다.")
            return True

        except OSError as error:
            print(f"기존 파일을 백업하지 못했습니다: {error}")
            return False

    def save_state(self):
        """현재 퀴즈와 최고 점수를 저장합니다."""

        data = {
            "quizzes": [
                quiz.to_dict() for quiz in self.quizzes
            ],
            "high_score": self.high_score,
            "high_score_correct": self.high_score_correct,
            "high_score_total": self.high_score_total,
            "score_history": self.score_history
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
        print("\n" + "=" * 40)
        print("       심신통합 헬스케어 퀴즈")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 퀴즈 삭제")
        print("5. 최고 점수 확인")
        print("6. 점수 기록 히스토리")
        print("7. 종료")
        print("=" * 40)

    def get_nonempty_input(self, message):
        while True:
            value = input(message).strip()

            if value:
                return value

            print("내용을 비워둘 수 없습니다. 다시 입력해 주세요.")

    def get_number_input(self, message, minimum, maximum):
        while True:
            value = input(message).strip()

            if not value:
                print("숫자를 입력해 주세요.")
                continue

            try:
                number = int(value)

                if minimum <= number <= maximum:
                    return number

                print(f"{minimum}~{maximum} 사이의 번호를 입력하세요.")

            except ValueError:
                print("숫자로 입력해 주세요.")

    def play_quiz(self):
        """퀴즈를 풀고 정답과 해설을 보여줍니다."""

        print("\n[심신통합 헬스케어 퀴즈 시작]")

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 2번 메뉴에서 퀴즈를 추가해 보세요.")
            return

        quizzes_to_play = self.quizzes.copy()
        random.shuffle(quizzes_to_play)

        max_count = len(quizzes_to_play)
        count = self.get_number_input(
            f"풀 문제 수를 입력하세요(1~{max_count}): ",
            1,
            max_count
        )
        quizzes_to_play = quizzes_to_play[:count]

        score = 0
        total = len(quizzes_to_play)

        for number, quiz in enumerate(quizzes_to_play, start=1):
            print("\n" + "-" * 40)
            print(f"문제 {number}. {quiz.question}")

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

            print(f"해설: {quiz.explanation}")

        percentage = score * 100 // total

        print("\n===== 퀴즈 결과 =====")
        print(f"총 문제 수: {total}")
        print(f"맞힌 문제 수: {score}")
        print(f"점수: {percentage}점")

        # 첫 기록이거나 기존 최고 점수보다 높으면 갱신합니다.
        if self.high_score_total == 0 or percentage > self.high_score:
            self.high_score = percentage
            self.high_score_correct = score
            self.high_score_total = total
            print("\n축하합니다! 최고 점수를 갱신했습니다.")

        self.score_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "correct": score,
            "total": total,
            "percentage": percentage
        })

        self.save_state()

    def add_quiz(self):
        """새로운 퀴즈와 해설을 추가합니다."""

        print("\n[새로운 퀴즈 추가]")

        question = self.get_nonempty_input("문제를 입력하세요: ")

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

        explanation = self.get_nonempty_input(
            "정답에 대한 해설을 입력하세요: "
        )

        new_quiz = Quiz(question, choices, answer, explanation)
        self.quizzes.append(new_quiz)

        print("\n새로운 퀴즈가 추가되었습니다!")
        print(f"현재 등록된 퀴즈 수: {len(self.quizzes)}개")

        self.save_state()

    def show_quizzes(self):
        """등록된 퀴즈와 해설을 보여줍니다."""

        print("\n" + "=" * 40)
        print("[심신통합 헬스케어 퀴즈 목록]")
        print(f"현재 등록된 퀴즈: {len(self.quizzes)}개")
        print("=" * 40)

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 2번 메뉴에서 퀴즈를 추가해 보세요.")
            return

        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[문제 {number}]")
            print(quiz.question)

            for i, choice in enumerate(quiz.choices, start=1):
                print(f"  {i}. {choice}")

            print(f"정답: {quiz.answer}번")
            print(f"해설: {quiz.explanation}")
            print("-" * 40)

        print("\n퀴즈 목록을 모두 확인했습니다.")

    def delete_quiz(self):
        """등록된 퀴즈를 번호로 선택해 삭제합니다."""

        print("\n[퀴즈 삭제]")

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        self.show_quizzes()

        index = self.get_number_input(
            f"삭제할 퀴즈 번호를 입력하세요(1~{len(self.quizzes)}): ",
            1,
            len(self.quizzes)
        )

        removed = self.quizzes.pop(index - 1)

        print(f"\n삭제되었습니다: {removed.question}")
        print(f"현재 등록된 퀴즈 수: {len(self.quizzes)}개")

        self.save_state()

    def show_high_score(self):
        """최고 점수를 보여줍니다."""

        print("\n===== 최고 점수 =====")

        if self.high_score_total == 0:
            print("아직 기록된 점수가 없습니다.")
        else:
            print(f"최고 점수: {self.high_score}점")
            print(
                f"정답 수: {self.high_score_correct}"
                f"/{self.high_score_total}문제"
            )

    def show_score_history(self):
        """지금까지 플레이한 모든 기록을 보여줍니다."""

        print("\n===== 점수 기록 히스토리 =====")

        if not self.score_history:
            print("아직 기록이 없습니다.")
            return

        for number, record in enumerate(self.score_history, start=1):
            print(
                f"[{number}] {record.get('timestamp', '-')}  "
                f"{record.get('correct', 0)}/{record.get('total', 0)}문제  "
                f"({record.get('percentage', 0)}점)"
            )

    def run(self):
        """프로그램을 실행합니다."""

        print("\n심신통합 헬스케어 퀴즈 게임에 오신 것을 환영합니다!")

        try:
            while True:
                self.show_menu()

                choice = self.get_number_input(
                    "메뉴 번호를 선택하세요: ",
                    1,
                    7
                )

                if choice == 1:
                    self.play_quiz()

                elif choice == 2:
                    self.add_quiz()

                elif choice == 3:
                    self.show_quizzes()

                elif choice == 4:
                    self.delete_quiz()

                elif choice == 5:
                    self.show_high_score()

                elif choice == 6:
                    self.show_score_history()

                elif choice == 7:
                    print("\n심신통합 헬스케어 퀴즈를 종료합니다.")
                    break

        except (KeyboardInterrupt, EOFError):
            print("\n\n입력이 중단되었습니다.")
            print("프로그램을 안전하게 종료합니다.")

        finally:
            self.save_state()
            print("데이터 저장을 확인했습니다.")


if __name__ == "__main__":
    try:
        game = QuizGame()
    except (KeyboardInterrupt, EOFError):
        # 데이터를 불러오는 도중 중단되어도 비정상 종료하지 않습니다.
        print("\n\n프로그램 시작이 중단되었습니다. 안전하게 종료합니다.")
    else:
        game.run()
