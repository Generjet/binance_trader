1. python 3.11 ashiglav
2. PostgreSQL hadgalah: tamir|Tamir4578 at 5432 port
3. MySQL hadgalah: root|Tamir4578 at 3306, tamir|T.mir4578
4. Шинээр data table column нэмэх бол save2mysql.py дотор шинэчилж бичнэ:
PS C:\Users\DELL\Documents\binanco\binance_trader\crypto_chart_app> python .\save2mysql.py table
гэж ажилуулна. Аргумент table нь table column-уудыг дахин үүсгэх функцийг дуудна.
Automating trade and becoming rich :)


def alter_table_add_columns():
    with app.app_context():
        db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_support BOOLEAN DEFAULT NULL"))
        db.session.execute(text("ALTER TABLE analyzed_data ADD COLUMN near_resistance BOOLEAN DEFAULT NULL"))
        db.session.commit()
        print("AnalyzedData table altered to add near_support and near_resistance columns.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        alter_table_add_columns() # Call alter_table_add_columns instead
        print("Database table alteration attempted.")
    else:
        create_database_if_not_exists() # Call create_database_if_not_exists for other cases
        print("Run with 'python save2mysql.py table' to update database tables.")
