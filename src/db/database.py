try:
    import psycopg2
    from psycopg2.extras import execute_batch
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

class DatabaseError(Exception):
    pass


class SalesDatabase:
    def __init__(self):
        self.conn = None

    def connect(self, host, port, dbname, user, password):
        if not HAS_PSYCOPG2:
            raise ImportError("Brak psycopg2. pip install psycopg2-binary")

        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )
            self.conn.autocommit = False

        except psycopg2.Error as e:
            raise DatabaseError(f"Błąd połączenia z bazą: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def is_connected(self) -> bool:
        return self.conn is not None

    def create_schema(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        product_id   VARCHAR(10) PRIMARY KEY,
                        name         VARCHAR(255) NOT NULL,
                        category     VARCHAR(100) NOT NULL,
                        unit_price   NUMERIC(10,2) NOT NULL CHECK (unit_price > 0)
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id           SERIAL PRIMARY KEY,
                        sale_date    DATE NOT NULL,
                        product_id   VARCHAR(10) NOT NULL REFERENCES products(product_id),
                        quantity     INTEGER NOT NULL CHECK (quantity >= 1),
                        seller       VARCHAR(255) NOT NULL,
                        region_code  CHAR(2) NOT NULL,
                        total_value  NUMERIC(12,2) NOT NULL
                    );
                """)

            self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"create_schema error: {e}")

    def drop_schema(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DROP TABLE IF EXISTS transactions;")
                cursor.execute("DROP TABLE IF EXISTS products;")

            self.conn.commit()

        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"drop_schema error: {e}")

    def import_dataset(self, dataset) -> int:
        try:
            with self.conn.cursor() as cursor:

                product_rows = [
                    (r.product.product_id,
                     r.product.name,
                     r.product.category,
                     r.product.price)
                    for r in dataset
                ]

                execute_batch(cursor, """
                    INSERT INTO products (product_id, name, category, unit_price)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (product_id) DO NOTHING
                """, product_rows)

                transaction_rows = [
                    (
                        r.date,
                        r.product.product_id,
                        r.quantity,
                        r.seller,
                        r.region,
                        r.total_value()
                    )
                    for r in dataset
                ]

                execute_batch(cursor, """
                    INSERT INTO transactions
                    (sale_date, product_id, quantity, seller, region_code, total_value)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, transaction_rows)

            self.conn.commit()
            return len(transaction_rows)

        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"import_dataset error: {e}")

    def get_revenue_by_category(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.category, SUM(t.total_value)
                    FROM transactions t
                    JOIN products p ON t.product_id = p.product_id
                    GROUP BY p.category
                    ORDER BY SUM(t.total_value) DESC
                """)
                return cursor.fetchall()

        except psycopg2.Error as e:
            raise DatabaseError(f"revenue_by_category error: {e}")

    def get_top_sellers(self, n=5):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT seller, SUM(total_value)
                    FROM transactions
                    GROUP BY seller
                    ORDER BY SUM(total_value) DESC
                    LIMIT %s
                """, (n,))
                return cursor.fetchall()

        except psycopg2.Error as e:
            raise DatabaseError(f"top_sellers error: {e}")

    def get_monthly_summary(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT TO_CHAR(sale_date, 'YYYY-MM') AS month,
                           SUM(total_value)
                    FROM transactions
                    GROUP BY month
                    ORDER BY month
                """)
                return cursor.fetchall()

        except psycopg2.Error as e:
            raise DatabaseError(f"monthly_summary error: {e}")

    def get_transaction_count(self) -> int:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM transactions;")
                return cursor.fetchone()[0]

        except psycopg2.Error as e:
            raise DatabaseError(f"transaction_count error: {e}")