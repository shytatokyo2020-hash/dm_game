from flask import Flask, render_template, request, jsonify
import numpy as np
import random

app = Flask(__name__)

# ======== 初期データ ========
bunmei = [' ', '火', '水', '光', '闇', '自然']
jyouken = ["進化クリーチャー","呪文","進化でないクリーチャー","クリーチャーでも呪文でもない","Wブレイカー","Tブレイカー","攻撃できない","スレイヤー","ブロッカー","スピードアタッカー","ガードマン（この問題はコストと文明に関しては条件を無視してよい）","ブロックされない","かっこいい","かわいい","C（コモン）","UC（アンコモン）","R（レア）","VR（ベリーレア）","SR（スーパーレア）","MAS（マスターレア、レジェンドレア、ビクトリーレア）","ドラゴン","コマンド","3つ以上の種族を持つ","G・0（この問題はコストと文明に関しては条件を無視してよい）","2回以上再録されたことがある","フェニックス（この問題はコストと文明に関しては条件を無視してよい）","殿堂カード（この問題はコストと文明に関しては条件を無視してよい）","シークレット版が存在する（この問題はコストと文明に関しては条件を無視してよい）","コスト軽減に関係する","特殊勝利（この問題はコストと文明に関しては条件を無視してよい）"]

results = {"success": 0, "fail": 0}



# 使用済み特性とモード設定
used_jyouken = []
unique_jyouken_mode = True  # ← Trueで「同じ特性が出ない」モード

# ======== ページ表示 ========
@app.route('/')
def index():
    return render_template('index.html', result=None)

# ======== 出題処理 ========
@app.route('/get_question', methods=['POST'])
def get_question():
    global jyouken, used_jyouken, unique_jyouken_mode

    # 文明をランダム生成（簡略化）
    arr_to_shuffle = np.arange(1, 6)
    np.random.shuffle(arr_to_shuffle)
    collor = arr_to_shuffle[:5]
    collorx = np.random.randint(0, 4)

    if collorx == 0:
        bun = bunmei[int(collor[0])]
    elif collorx == 1:
        bun = f"{bunmei[int(collor[1])]}かつ{bunmei[int(collor[0])]}"
    elif collorx == 2:
        bun = f"{bunmei[int(collor[2])]}かつ{bunmei[int(collor[1])]}かつ{bunmei[int(collor[0])]}"
    else:
        bun = "五文明orゼロ文明"

    # コスト条件生成
    cost_sf = np.arange(1, 11)
    np.random.shuffle(cost_sf)
    costunder, costupper = sorted(cost_sf[:2])
    cost_str = f"コスト{costunder}～コスト{costupper}" if costupper < 10 else "コスト10以上"

    # 特性条件（重複なしモード）
    if unique_jyouken_mode:
        # もし全特性が使い切られていたらリセット
        if not jyouken:
            jyouken.extend(used_jyouken)
            used_jyouken.clear()
            print("★ jyoukenリセット:", jyouken)

        # 残りの中からランダムに1つ選ぶ
        jy_str = random.choice(jyouken)
        # 使用済みリストへ移動
        used_jyouken.append(jy_str)
        jyouken.remove(jy_str)

    else:
        # 通常モード（重複あり）
        jy_str = random.choice(jyouken)

    print("現在の jyouken:", jyouken)
    print("使用済み used_jyouken:", used_jyouken)
    print("今回の特性:", jy_str)

    return jsonify({
        "bunmei": bun,
        "cost": cost_str,
        "jyouken": jy_str
    })

# ======== 入力フォームからの条件追加 ========
@app.route('/submit', methods=['POST'])
def submit():
    global jyouken
    conditions_text = request.form.get('conditions', '')
    new_conditions = [line.strip() for line in conditions_text.split('\n') if line.strip()]
    added = []

    for cond in new_conditions:
        if cond not in jyouken:
            jyouken.append(cond)
            added.append(cond)

    print("追加後の jyouken:", jyouken)
    return render_template('index.html', result=f"{len(added)}個の条件を追加しました！（合計 {len(jyouken)} 個）")

@app.route('/record_result', methods=['POST'])
def record_result():
    global results
    data = request.get_json()
    if data["result"] == "success":
        results["success"] += 1
    elif data["result"] == "fail":
        results["fail"] += 1
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
