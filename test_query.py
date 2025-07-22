from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("mysql+pymysql://root:@localhost:3306/pos_ai")

query1 = "SELECT COUNT(*) FROM users;"
query2 = "SELECT id, created_at FROM orders ORDER BY created_at DESC LIMIT 5;"

print("User Count:", db.run(query1))
print("Recent Orders:", db.run(query2))
