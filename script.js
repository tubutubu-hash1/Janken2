let stats = {
  wins: 0,
  losses: 0,
  draws: 0,
  totalGames: 0,
  history: [] // 履歴を保存
};

const hands = ["rock", "paper", "scissors"];
let playerId = null; // プレイヤーIDを保存するグローバル変数

// ダブルタップでの拡大防止
document.addEventListener("dblclick", (e) => e.preventDefault());

// リセットボタンの動作
function resetGame() {
  fetch("http://127.0.0.1:5000/reset", {
    method: "POST",
  })
    .then(response => response.json())
    .then(data => {
      console.log(data.message);

      // フロントエンドの状態リセット
      stats = { wins: 0, losses: 0, draws: 0, totalGames: 0, history: [] };
      playerId = null; // プレイヤーIDもリセット
      updateStats();
      updateHistoryTable();
      alert("ゲームがリセットされました！");
    })
    .catch(err => {
      console.error("リセット中にエラーが発生しました:", err);
    });
}

// プレイの処理
function play(playerHand) {
  // 最初の1回だけプレイヤーIDを取得
  if (!playerId) {
    playerId = prompt("プレイヤーIDを入力してください:");
    if (!playerId) {
      alert("プレイヤーIDを入力してください。");
      return;
    }
  }

  const computerHand = hands[Math.floor(Math.random() * hands.length)];
  const result = getResult(playerHand, computerHand);

  const payload = {
    player_id: playerId,
    player_hand: playerHand,
    computer_hand: computerHand,
    result: result
  };

  fetch("http://127.0.0.1:5000/play", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
    .then(response => response.json())
    .then(data => {
      console.log(data.message);
      console.log(`次の手の予測: ${data.predicted_next_hand}`);
      alert(`コンピューターの手: ${computerHand}\n結果: ${result}\n次の予測: ${data.predicted_next_hand}`);

      // ローカルの統計データ更新
      stats.totalGames++;
      if (result === "win") stats.wins++;
      if (result === "loss") stats.losses++;
      if (result === "draw") stats.draws++;
      stats.history.push({ playerHand, computerHand, result });

      // UI更新
      updateStats();
      updateHistoryTable();
    })
    .catch(err => {
      console.error("ゲームプレイ中にエラーが発生しました:", err);
    });
}

// 勝敗判定
function getResult(player, computer) {
  if (player === computer) return "draw";
  if (
    (player === "rock" && computer === "scissors") ||
    (player === "scissors" && computer === "paper") ||
    (player === "paper" && computer === "rock")
  ) {
    return "win";
  }
  return "loss";
}

// 統計データのUI更新
function updateStats() {
  document.getElementById("total-games").textContent = stats.totalGames;
  document.getElementById("wins").textContent = stats.wins;
  document.getElementById("losses").textContent = stats.losses;
  document.getElementById("draws").textContent = stats.draws;
}

// 履歴テーブルのUI更新
function updateHistoryTable() {
  const tableBody = document.getElementById("history-table").querySelector("tbody");
  tableBody.innerHTML = ""; // テーブルをクリア
  stats.history.forEach((entry, index) => {
    const row = tableBody.insertRow();
    row.insertCell().textContent = index + 1;
    row.insertCell().textContent = entry.playerHand;
    row.insertCell().textContent = entry.computerHand;
    row.insertCell().textContent = entry.result;
  });
}
