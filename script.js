function play(playerHand) {
  const playerId = prompt("プレイヤーIDを入力してください:");
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
      updateStats();
      updateHistoryTable();
    });
}
