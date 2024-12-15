from flask import Flask, request, jsonify
import openpyxl
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import os

app = Flask(__name__)

# Excelファイル名
EXCEL_FILE = "history.xlsx"

# 履歴データフレーム
df = pd.DataFrame(columns=["player_id", "player_hand", "computer_hand", "result"])

# 手のマッピング
hand_mapping = {"rock": 0, "paper": 1, "scissors": 2}
reverse_hand_mapping = {v: k for k, v in hand_mapping.items()}

# Excelファイルが存在しない場合、新規作成
if not os.path.exists(EXCEL_FILE):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "じゃんけん履歴"
    ws.append(["player_id", "player_hand", "computer_hand", "result"])  # ヘッダー行
    wb.save(EXCEL_FILE)

# サーバー起動時にExcelデータをロード
def load_excel():
    global df
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name="じゃんけん履歴")

load_excel()

# Excelに保存
def save_to_excel(player_id, player_hand, computer_hand, result):
    global df
    new_entry = pd.DataFrame([{
        "player_id": player_id,
        "player_hand": player_hand,
        "computer_hand": computer_hand,
        "result": result
    }])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, sheet_name="じゃんけん履歴")

# 機械学習モデルをトレーニング
def train_model(player_id):
    player_data = df[df["player_id"] == player_id]

    if len(player_data) < 5:  # 最低限のデータ数が必要
        return None

    # 手のマッピングを適用
    player_data["player_hand"] = player_data["player_hand"].map(hand_mapping)
    player_data["computer_hand"] = player_data["computer_hand"].map(hand_mapping)

    # 特徴量とラベルを分ける
    X = player_data[["player_hand", "computer_hand"]]
    y = player_data["player_hand"].shift(-1).fillna(player_data["player_hand"]).astype(int)  # 次の手を予測

    # モデルのトレーニング
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    return model

@app.route('/play', methods=['POST'])
def play():
    global df

    # クライアントからデータを受け取る
    data = request.json
    player_id = data["player_id"]
    player_hand = data["player_hand"]
    computer_hand = data["computer_hand"]
    result = data["result"]

    # Excelに保存
    save_to_excel(player_id, player_hand, computer_hand, result)

    # プレイヤー固有のモデルをトレーニング
    model = train_model(player_id)
    predicted_next_hand = None

    if model:
        # 最新の手を使って次の手を予測
        current_hand = hand_mapping[player_hand]
        computer_hand_value = hand_mapping[computer_hand]
        predicted_next_hand = model.predict([[current_hand, computer_hand_value]])[0]
        predicted_next_hand = reverse_hand_mapping[predicted_next_hand]

    return jsonify({
        "message": f"Result saved for player {player_id}.",
        "predicted_next_hand": predicted_next_hand
    })

@app.route('/reset', methods=['POST'])
def reset_game():
    global df
    df = pd.DataFrame(columns=["player_id", "player_hand", "computer_hand", "result"])
    if os.path.exists(EXCEL_FILE):
        os.remove(EXCEL_FILE)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "じゃんけん履歴"
    ws.append(["player_id", "player_hand", "computer_hand", "result"])  # ヘッダー行
    wb.save(EXCEL_FILE)
    return jsonify({"message": "Game reset and Excel file cleared."})

if __name__ == "__main__":
    app.run(debug=True)
