from flask import Flask, render_template, request, redirect
import sqlite3


app = Flask(__name__)


# DB 연결
def get_db():
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row
    return conn


# 글을 저장할 테이블 생성
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


create_table()


# 글 목록과 검색
@app.route("/")
def home():
    keyword = request.args.get("keyword", "")
    conn = get_db()

    if keyword:
        posts = conn.execute(
            "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
    else:
        posts = conn.execute(
            "SELECT * FROM posts ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template("index.html", posts=posts, keyword=keyword)


# 글 작성
@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = get_db()
        conn.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (title, content)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("write.html")


# 글 상세보기
@app.route("/post/<int:post_id>")
def post(post_id):
    conn = get_db()
    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    ).fetchone()
    conn.close()

    if post is None:
        return "글을 찾을 수 없습니다.", 404

    return render_template("post.html", post=post)


# 서버 실행
if __name__ == "__main__":
    app.run(debug=True)
