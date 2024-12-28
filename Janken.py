from flask import Flask, render_template, request, redirect
import pandas as pd
import random
import os

app = Flask(__name__)

# Excelファイルのパス
EXCEL_FILE = "results.xlsx"

# 初期化: Excelファイルが存在しない場合は作成
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["User Choice", "AI Choice", "Result"])
    df.to_excel(EXCEL_FILE, index=False)

# 勝敗の判定
def judge(user_choice, ai_choice):
    if user_choice == ai_choice:
        return "Draw"
    elif (user_choice == "Rock" and ai_choice == "Scissors") or \
         (user_choice == "Paper" and ai_choice == "Rock") or \
         (user_choice == "Scissors" and ai_choice == "Paper"):
        return "Win"
    else:
        return "Lose"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # ユーザーの選択を取得
        user_choice = request.form["choice"]
        # AIの選択をランダムで決定
        ai_choice = random.choice(["Rock", "Paper", "Scissors"])
        # 勝敗判定
        result = judge(user_choice, ai_choice)
        
        # 結果をExcelに保存
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([{"User Choice": user_choice, "AI Choice": ai_choice, "Result": result}])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        # 結果をページに表示
        return render_template("index.html", user_choice=user_choice, ai_choice=ai_choice, result=result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
