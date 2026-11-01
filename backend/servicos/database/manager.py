
from typing import Any
import psycopg2
from psycopg2.extras import DictCursor


class DatabaseManager:
    """Classe de gerenciamento do database."""

    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            dbname="ProjetoBD",
            user="postgres",
            password="123",
            host="127.0.0.1",
            port=5432,
        )

        self.cursor = self.conn.cursor(
            cursor_factory=DictCursor
        )

    def execute_statement(
        self,
        statement: str,
        params: tuple | None = None
    ) -> bool:
        """Executa INSERT, UPDATE, DELETE etc."""

        try:
            self.cursor.execute(statement, params)
            self.conn.commit()
            return True

        except psycopg2.Error as error:
            print(f"Erro no banco: {error}")
            self.conn.rollback()
            return False

    def execute_select_all(
        self,
        query: str,
        params: tuple | None = None
    ) -> list[dict[str, Any]]:
        """Executa SELECT retornando todas as linhas."""

        self.cursor.execute(query, params)

        return [
            dict(item)
            for item in self.cursor.fetchall()
        ]

    def execute_select_one(
        self,
        query: str,
        params: tuple | None = None
    ) -> dict | None:
        """Executa SELECT retornando uma única linha."""

        self.cursor.execute(query, params)

        result = self.cursor.fetchone()

        if not result:
            return None

        return dict(result)
    
    def execute_transaction(
        self,
        operations: list[tuple[str, tuple | None]]
    ) -> bool:
        """
        Executa múltiplas operações (INSERT, UPDATE, DELETE) em uma única transação.
        operations: Lista de tuplas no formato (query, params).
        Faz commit se todas passarem, ou rollback se qualquer uma falhar.
        """
        try:
            for statement, params in operations:
                self.cursor.execute(statement, params)
            
            self.conn.commit()
            return True

        except psycopg2.Error as error:
            print(f"Erro na transação: {error}")
            self.conn.rollback()
            raise error  # Levanta o erro para o try/except da rota capturar

    def close(self) -> None:
        """Fecha cursor e conexão."""

        self.cursor.close()
        self.conn.close()
