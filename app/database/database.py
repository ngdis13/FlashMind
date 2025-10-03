import sqlite3
from datetime import datetime


class SimpleDB:
    """Класс управляющий базой данных"""

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

    # Функции для работы с темами карточек
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

    def update_topic(self, topic_id, name=None, description=None):
        """Функция для обновления существующей темы

        Args:
            topic_id (int): id темы
            name (str, optional): Название темы. Defaults to None.
            description (str, optional): Описание темы. Defaults to None.

        Returns:
            object: возвращает обновленный обьект с информацией о теме
        """
        now = datetime.now().isoformat()
        update_fields = []
        params = []
        if name:
            update_fields.append("name = ?")
            params.append(name)
        if description:
            update_fields.append("description = ?")
            params.append(description)

        update_fields.append("updated_at = ?")
        params.append(now)
        params.append(topic_id)

        if update_fields:
            query = f"UPDATE topics SET {', '.join(update_fields)} WHERE id = ?"
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.get_topic(topic_id)
        return None

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

    # Функции для работы с карточками
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

    def update_flashcard(
        self, flashcard_id, topic_id=None, question=None, answer=None, difficulty_level=None, last_reviewed_at=None
    ):
        now = datetime.now().isoformat()
        update_fields = []
        params = []

        if topic_id:
            update_fields.append("topic_id = ?")
            params.append(topic_id)

        if question:
            update_fields.append("question = ?")
            params.append(question)

        if answer:
            update_fields.append("answer = ?")
            params.append(answer)

        if difficulty_level:
            update_fields.append("difficulty_level = ?")
            params.append(difficulty_level)

        if last_reviewed_at:
            update_fields.append("last_reviewed_at = ?")
            params.append(last_reviewed_at)

        update_fields.append("updated_at = ?")
        params.append(now)
        params.append(flashcard_id)

        if update_fields:
            query = f"UPDATE flashcards SET {', '.join(update_fields)} WHERE id = ?"
            self.cursor.execute(query, flashcard_id)
            self.conn.commit()
            return self.get_flashcard(flashcard_id)
        return None

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
