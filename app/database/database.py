import sqlite3
from datetime import datetime


class SimpleDB:
    """Класс упарвляющий базой данных"""

    def __init__(self, db_file="flashcards.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Функция для создания таблиц"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY,
                topic_id INTEGER,
                question TEXT,
                answer TEXT,
                difficulty_level INTEGER,
                last_reviewed_at TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """
        )

        self.conn.commit()

    def close(self):
        """Функция для закрытия базы данных"""
        self.conn.close()

    def get_all_topics(self):
        """Функция, возвращающая список тем

        Returns:
            object : список тем из файла
        """
        self.cursor.execute("SELECT * FROM topics")
        return self.cursor.fetchall()

    def get_topic(self, topic_id):
        """Функция, которая возвращает тему с заданным topic_id из таблицы topics

        Args:
            topic_id (int): номер темы

        Returns:
            object | None: кортеж с записью темы
        """
        self.cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        return self.cursor.fetchone()

    def get_topic_by_name(self, name):
        """Функция, которая возвращает тему с заданным именем из таблицы topics

        Args:
            name (str): название темы

        Returns:
            object | None: кортеж с записью темы, если найдена, иначе None
        """
        self.cursor.execute("SELECT * FROM topics WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def create_topic(self, name, description=None):
        """Функция, которая создает новую тему в таблице topics
        Если тема с таким именем уже существует, возвращает существующую тему.

        Args:
            name (str): название темы
            description (str): описание темы
        Returns:
            object: cозданная тема
        """
        check_topic = self.get_topic_by_name(name)
        if check_topic:
            return check_topic

        now = datetime.now().isoformat()
        self.cursor.execute(
            """
            INSERT INTO topics(name, description, created_at, updated_at)
            VALUES(?, ?, ?, ?)
            """,
            (name, description, now, now),
        )
        self.conn.commit()
        return self.get_topic(self.cursor.lastrowid)

    def delete_topic(self, topic_id):
        """Удаляет тему по id

        Args:
            topic_id (int): номер темы

        Returns:
            boolean: возвращает true, если тема была удаленаб false в противоположном случае
        """
        self.cursor.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        self.conn.commit()
        # информирование о том что тема была удалена
        return self.cursor.rowcount > 0

    def get_all_flashcards(self):
        """Функция, возвращающая все существующие карточки

        Returns:
            object: массив с информацией о каждой карточке
        """
        self.cursor.execute("SELECT * FROM flashcards")
        return self.cursor.fetchall()

    def get_flashcard(self, flashcard_id):
        """Функция возращающая карточку по id

        Args:
            flashcard_id (int): id карточки

        Returns:
            object: содержимое карточки
        """
        self.cursor.execute("SELECT * FROM flashcards WHERE id = ?", (flashcard_id,))
        return self.cursor.fetchone()

    def get_flashcard_by_question(self, flashcard_question):
        """Функция возращающая карточку по question

        Args:
            flashcard_name (int): name карточки

        Returns:
            object: содержимое карточки
        """
        self.cursor.execute("SELECT * FROM flashcards WHERE question = ?", (flashcard_question,))
        return self.cursor.fetchone()

    def create_flashcard(self, topic_id, question, answer, difficulty_level=1):
        """Функция создающая новую карточку

        Args:
            topic_id (int): id темы карточки
            question (int): вопрос
            answer (int): ответ на вопрос
            difficulty_level (int): уровень сложности карточки

        Returns:
            object: созданная карточка
        """
        check_flashcard = self.get_flashcard_by_question(question)
        if check_flashcard:
            return check_flashcard

        now = datetime.now().isoformat()
        self.cursor.execute(
            """
                INSERT INTO flashcards(topic_id, question, answer, difficulty_level, last_reviewed_at, created_at, updated_at) VALUES(?, ?, ?, ?, NULL, ?, ?)
            """,
            (topic_id, question, answer, difficulty_level, now, now),
        )
        self.conn.commit()
        return self.get_flashcard(self.cursor.lastrowid)

    def get_flashcards_by_topic(self, topic_id):
        """Возвращает все карточки в определенной теме

        Args:
            topic_id (int): номер темы

        Returns:
            object: массив с информацией о каждой карточке по определенной теме
        """
        self.cursor.execute("SELECT * FROM flashcards WHERE topic_id = ?", (topic_id,))
        return self.cursor.fetchall()

    def delete_flashcard(self, flashcard_id):
        """Удаляет карточку по id

        Args:
            flashcard_id (int): id карточки

        Returns:
            boolean: возвращает true если карточка была удалена, false в противоположном случае
        """
        self.cursor.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0


if __name__ == "__main__":
    database = SimpleDB()
    database.create_topic("Основы реляционных баз данных", "Тема, посвященная основам реляционных баз данных")
    database.create_topic("Математический анализ", "Основные понятия")
    database.delete_topic(2)
    database.create_flashcard(
        3,
        "Что такое предел последовательности?",
        "Число b является пределом числовой последовательности {aₙ}, если для любого сколь угодно малого положительного числа ε (эпсилон) найдется такое натуральное число N, что для всех номеров n > N будет выполняться условие |aₙ - b| < ε. ",
        2,
    )
    print(database.get_flashcards_by_topic(3))
