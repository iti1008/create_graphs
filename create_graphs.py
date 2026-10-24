"""課題3.csv から円グラフ・棒グラフ・ヒストグラムを作成し、PNG 画像として保存する。"""
import csv
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

import matplotlib

matplotlib.use("Agg")  # 画面表示せずファイルに保存する
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "課題3.csv"

# 日本語フォント（macOS 標準のヒラギノ）
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro", "sans-serif"]
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
# 文字サイズ全体を大きめに設定
plt.rcParams["font.size"] = 15
plt.rcParams["xtick.labelsize"] = 15
plt.rcParams["ytick.labelsize"] = 15
plt.rcParams["legend.fontsize"] = 15
plt.rcParams["legend.title_fontsize"] = 15

# 色覚多様性に配慮したカテゴリカルカラー（固定順）
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
TEXT = "#0b0b0b"
GRID = "#dddcd8"
NOTE = "#52514e"
# 円グラフの文字色：背景色とのコントラストを確保（青・橙は白、緑・黄は黒）
PIE_TEXT_COLORS = ["white", "white", TEXT, TEXT]


def set_horizontal_ylabel(ax, text):
    """Y軸ラベルを横書きにし、軸の上端（左上）に配置する。"""
    ax.set_ylabel(text, rotation=0, fontsize=17, ha="left", va="bottom")
    ax.yaxis.set_label_coords(-0.08, 1.03)


def load_data(path):
    """CSV を読み込み、[{名前, 所属, スコア}, ...] を返す。"""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [
            {"名前": row["名前"], "所属": row["所属"], "スコア": int(row["スコア"])}
            for row in csv.DictReader(f)
        ]


def pie_chart(data):
    """所属ごとの参加者数と割合を円グラフで表示する。"""
    counts = Counter(r["所属"] for r in data).most_common()
    sizes = [v for _, v in counts]
    total = sum(sizes)

    fig, ax = plt.subplots(figsize=(9, 9.6))
    wedges, _ = ax.pie(
        sizes,
        colors=COLORS[: len(counts)],
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 3},
    )
    # 所属名・割合・人数を扇形の中にまとめて表示する（凡例と見比べる手間をなくす）
    for wedge, (name, n), text_color in zip(wedges, counts, PIE_TEXT_COLORS):
        angle = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        x, y = 0.6 * np.cos(angle), 0.6 * np.sin(angle)
        ax.text(x, y - 0.02, f"{name}\n{n / total * 100:.1f}%", ha="center", va="center",
                fontsize=24, fontweight="bold", color=text_color, linespacing=1.3)
        ax.text(x, y - 0.22, f"（{n}人）", ha="center", va="center", fontsize=18, color=text_color)

    ax.set_title(f"所属別の参加者数の割合（全{total}人）", fontsize=24, pad=20)
    ax.axis("equal")
    fig.text(0.5, 0.03, "※ 割合は小数第2位を四捨五入しているため、合計が100%にならない場合があります。",
             ha="center", fontsize=14, color=NOTE)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(BASE_DIR / "pie_chart.png", dpi=150)
    plt.close(fig)


def bar_chart(data):
    """所属ごとの平均点を棒で、最高点〜最低点の範囲を縦線で表示する。"""
    scores = defaultdict(list)
    for r in data:
        scores[r["所属"]].append(r["スコア"])
    depts = sorted(scores, key=lambda d: mean(scores[d]), reverse=True)
    avgs = [mean(scores[d]) for d in depts]
    highs = [max(scores[d]) for d in depts]
    lows = [min(scores[d]) for d in depts]
    overall = mean(r["スコア"] for r in data)
    x = list(range(len(depts)))

    fig, ax = plt.subplots(figsize=(12, 8.6))
    # 棒の長さが点数に比例するよう、Y軸は 0 点から始める
    ax.bar(x, avgs, width=0.55, color=COLORS[0], zorder=3, label="平均点（棒）")
    ax.errorbar(
        x, avgs,
        yerr=[[a - lo for a, lo in zip(avgs, lows)], [hi - a for a, hi in zip(avgs, highs)]],
        fmt="none", ecolor=TEXT, elinewidth=2, capsize=12, capthick=2, zorder=4,
        label="最低点〜最高点の範囲（縦線）",
    )
    for xi, a, hi, lo in zip(x, avgs, highs, lows):
        ax.text(xi, a / 2, f"平均\n{a:.1f}点", ha="center", va="center",
                fontsize=20, fontweight="bold", color="white", linespacing=1.3, zorder=5)
        # 最高・最低の値は棒の右外側、縦線の端と同じ高さに置く（白背景で破線と重なっても読める）
        for value, label in ((hi, "最高"), (lo, "最低")):
            ax.text(xi + 0.3, value, f"{label} {value}", ha="left", va="center", fontsize=15, color=TEXT,
                    zorder=5, bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none"})
    ax.axhline(overall, color=COLORS[1], linestyle="--", linewidth=2, zorder=2,
               label=f"全体平均 {overall:.1f}点（破線）")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{d}\n({len(scores[d])}人)" for d in depts], fontsize=17)
    ax.set_title("所属別のスコア（平均点と最高・最低点）", fontsize=24, pad=50)
    ax.set_xlabel("所属（平均点の高い順）", fontsize=17, labelpad=10)
    set_horizontal_ylabel(ax, "スコア（点）")
    ax.set_ylim(0, 105)
    ax.set_yticks(range(0, 101, 10))
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False, fontsize=14,
              handlelength=1.5, columnspacing=1.5)
    fig.tight_layout()
    fig.savefig(BASE_DIR / "bar_chart.png", dpi=150)
    plt.close(fig)


def histogram(data):
    """全参加者のスコア分布をヒストグラムで表示する。"""
    values = [r["スコア"] for r in data]
    avg = mean(values)
    # 5 点刻みのビン（70〜100 点 → 6 ビン。スタージェスの公式 1+log2(35)≈6.1 とも一致）
    bins = list(range(70, 101, 5))

    fig, ax = plt.subplots(figsize=(12, 8.6))
    counts, _, patches = ax.hist(values, bins=bins, color=COLORS[0], edgecolor="white", linewidth=2, zorder=3)
    ax.bar_label(patches, labels=[f"{int(c)}人" for c in counts], padding=4, fontsize=17, color=TEXT)
    ax.axvline(avg, color=TEXT, linestyle="--", linewidth=2, zorder=4)
    # 平均線が 85 の境界と紛れないよう、線の横に値を直接表示する
    ax.annotate(
        f"平均 {avg:.1f}点",
        xy=(avg, max(counts) + 1.2),
        xytext=(-10, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        fontsize=17,
        fontweight="bold",
        color=TEXT,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "none"},
        zorder=5,
    )

    ax.set_title(f"スコアの分布（全{len(values)}人）", fontsize=24, pad=50)
    ax.set_xlabel("スコア（点）", fontsize=17, labelpad=10)
    set_horizontal_ylabel(ax, "人数（人）")
    ax.set_xticks(bins)
    ax.set_ylim(0, max(counts) + 2)
    ax.grid(axis="y", color=GRID, zorder=0)
    # ビン境界の扱い（matplotlib の仕様）を注記する
    fig.text(
        0.5, 0.02,
        "※ 各区間は「下限以上・上限未満」（例：80点は80〜85の区間に含む）。最後の95〜100のみ100点を含む。",
        ha="center", fontsize=14, color=NOTE,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(BASE_DIR / "histogram.png", dpi=150)
    plt.close(fig)


def main():
    data = load_data(CSV_PATH)
    pie_chart(data)
    bar_chart(data)
    histogram(data)
    print(f"{len(data)} 件のデータからグラフを作成しました: pie_chart.png, bar_chart.png, histogram.png")


if __name__ == "__main__":
    main()
