# 심신통합 헬스케어 퀴즈 게임 자동 테스트
# 실행 방법: py -m unittest -v   (macOS/Linux: python3 -m unittest -v)
# 실제 state.json은 건드리지 않고, 임시 폴더의 파일로만 테스트합니다.

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import main


class QuizGameTestCase(unittest.TestCase):
    """테스트마다 임시 state.json 경로를 사용하도록 설정합니다."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        folder = Path(self.temp_dir.name)
        self.data_file = folder / "state.json"
        self.backup_file = folder / "state.json.bak"

        self.patches = [
            mock.patch.object(main, "DATA_FILE", self.data_file),
            mock.patch.object(main, "BACKUP_FILE", self.backup_file),
        ]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        self.temp_dir.cleanup()

    def make_game(self):
        """화면 출력 없이 게임 객체를 만듭니다."""

        with redirect_stdout(io.StringIO()):
            return main.QuizGame()

    def run_with_inputs(self, method, inputs):
        """정해진 입력으로 메서드를 실행하고 화면 출력을 돌려줍니다."""

        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=list(inputs)):
            with redirect_stdout(output):
                method()
        return output.getvalue()

    def read_saved(self):
        with open(self.data_file, "r", encoding="utf-8") as file:
            return json.load(file)


class TestQuiz(unittest.TestCase):
    def test_to_dict(self):
        quiz = main.Quiz("문제", ["a", "b", "c", "d"], 2, "해설")
        self.assertEqual(
            quiz.to_dict(),
            {
                "question": "문제",
                "choices": ["a", "b", "c", "d"],
                "answer": 2,
                "explanation": "해설",
            },
        )


class TestInput(QuizGameTestCase):
    def test_number_input_retries_until_valid(self):
        game = self.make_game()
        # 빈 입력, 문자, 범위 밖 숫자 다음에 공백이 섞인 올바른 숫자를 입력
        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=["", "abc", "9", "0", " 3 "]):
            with redirect_stdout(output):
                result = game.get_number_input("선택: ", 1, 7)

        self.assertEqual(result, 3)
        text = output.getvalue()
        self.assertIn("숫자를 입력해 주세요.", text)
        self.assertIn("숫자로 입력해 주세요.", text)
        self.assertEqual(text.count("1~7 사이의 번호를 입력하세요."), 2)

    def test_nonempty_input_rejects_blank(self):
        game = self.make_game()
        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=["   ", "내용"]):
            with redirect_stdout(output):
                result = game.get_nonempty_input("문제: ")

        self.assertEqual(result, "내용")
        self.assertIn("비워둘 수 없습니다", output.getvalue())


class TestStateFile(QuizGameTestCase):
    def test_first_run_uses_default_quizzes(self):
        game = self.make_game()
        self.assertEqual(len(game.quizzes), 5)
        self.assertTrue(self.data_file.exists())

    def test_corrupted_file_is_backed_up_and_reset(self):
        self.data_file.write_text("{broken", encoding="utf-8")
        game = self.make_game()

        self.assertEqual(len(game.quizzes), 5)
        self.assertEqual(game.high_score, 0)
        self.assertEqual(
            self.backup_file.read_text(encoding="utf-8"), "{broken"
        )

    def test_saved_data_survives_restart(self):
        game = self.make_game()
        self.run_with_inputs(
            game.add_quiz,
            ["새 문제", "1번", "2번", "3번", "4번", "2", "새 해설"],
        )

        restarted = self.make_game()
        self.assertEqual(len(restarted.quizzes), 6)
        self.assertEqual(restarted.quizzes[-1].question, "새 문제")
        self.assertEqual(restarted.quizzes[-1].answer, 2)

    def test_empty_quiz_list_is_not_treated_as_corrupted(self):
        game = self.make_game()
        game.high_score, game.high_score_total = 80, 5
        game.quizzes = []
        game.save_state()

        restarted = self.make_game()
        self.assertEqual(restarted.quizzes, [])
        self.assertEqual(restarted.high_score, 80)
        self.assertFalse(self.backup_file.exists())


class TestPlayAndScore(QuizGameTestCase):
    def test_play_updates_high_score_and_history(self):
        game = self.make_game()
        # 랜덤 순서를 고정해서 정답을 미리 알 수 있게 합니다.
        with mock.patch("main.random.shuffle"):
            answers = [str(quiz.answer) for quiz in game.quizzes]
            output = self.run_with_inputs(game.play_quiz, ["5"] + answers)

        self.assertIn("점수: 100점", output)
        self.assertEqual(game.high_score, 100)
        self.assertEqual(self.read_saved()["high_score"], 100)
        self.assertEqual(len(self.read_saved()["score_history"]), 1)

    def test_zero_score_is_recorded_as_first_score(self):
        game = self.make_game()
        wrong = str(game.quizzes[0].answer % 4 + 1)
        with mock.patch("main.random.shuffle"):
            self.run_with_inputs(game.play_quiz, ["1", wrong])

        self.assertEqual(game.high_score_total, 1)
        output = self.run_with_inputs(game.show_high_score, [])
        self.assertIn("최고 점수: 0점", output)

    def test_no_quizzes(self):
        game = self.make_game()
        game.quizzes = []
        self.assertIn("등록된 퀴즈가 없습니다", self.run_with_inputs(game.play_quiz, []))
        self.assertIn("등록된 퀴즈가 없습니다", self.run_with_inputs(game.show_quizzes, []))

    def test_no_score_yet(self):
        game = self.make_game()
        output = self.run_with_inputs(game.show_high_score, [])
        self.assertIn("아직 기록된 점수가 없습니다.", output)


class TestDeleteAndExit(QuizGameTestCase):
    def test_delete_quiz_is_saved(self):
        game = self.make_game()
        first_question = game.quizzes[0].question
        self.run_with_inputs(game.delete_quiz, ["1"])

        saved = self.read_saved()["quizzes"]
        self.assertEqual(len(saved), 4)
        self.assertNotIn(first_question, [q["question"] for q in saved])

    def test_ctrl_c_and_eof_exit_safely(self):
        for error in (KeyboardInterrupt, EOFError):
            with self.subTest(error=error.__name__):
                game = self.make_game()
                output = io.StringIO()
                with mock.patch("builtins.input", side_effect=error):
                    with redirect_stdout(output):
                        game.run()  # 예외가 밖으로 나오지 않아야 합니다.
                self.assertIn("안전하게 종료합니다", output.getvalue())
                self.assertTrue(self.data_file.exists())


if __name__ == "__main__":
    unittest.main()
