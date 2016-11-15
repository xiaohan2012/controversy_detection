conn = new Mongo();
db = conn.getDB("controversy");
print(db.test.find().count());
