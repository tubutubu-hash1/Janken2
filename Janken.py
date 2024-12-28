from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import os

app = Flask(__name__)

# Excelファイルのパス
EXCEL_FILE = "result.xlsx"

# 初期化: Excelファイルがなければ作成
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["Player", "AI", "Result"])
    df.to_excel(EXCEL_FILE, index=False)

# AIの手をランダムに生成
def get_ai_choice():
    return random.choice(["グー", "チョキ", "パー"])

# 勝敗判定
def judge(player, ai):
    if player == ai:
        return "引き分け"
    elif (player == "グー" and ai == "チョキ") or \
         (player == "チョキ" and ai == "パー") or \
         (player == "パー" and ai == "グー"):
        return "勝ち"
    else:
        return "負け"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play():
    # プレイヤーの手を受け取る
    player_choice = request.json.get("player")
    ai_choice = get_ai_choice()
    result = judge(player_choice, ai_choice)

    # 結果をExcelに記録
    df = pd.read_excel(EXCEL_FILE)
    new_row = {"Player": player_choice, "AI": ai_choice, "Result": result}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

    return jsonify({"player": player_choice, "ai": ai_choice, "result": result})

if __name__ == "__main__":
    app.run(debug=True)
