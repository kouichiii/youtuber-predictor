# YouTuber Growth Predictor

YouTuberの半年後の登録者増加率を予測するアプリケーション。

## 機能

### 公開アプリ（frontend）
- **成長予測ランキング**: 半年後の成長率を予測し、ランキング表示
- **チャンネル詳細**: 予測に使用した特徴量、統計推移グラフ、関連ニュースを表示
- **ニュース一覧**: YouTuber関連ニュースをカテゴリ別に表示

### 管理画面（frontend-admin）
- **チャンネル管理**: YouTubeからチャンネルを検索して追加・削除
- **ジョブ実行**: データ収集・予測・学習をWebから実行

## 技術スタック

### バックエンド
- Python 3.10+
- FastAPI
- SQLAlchemy (SQLite)
- LightGBM (機械学習)

### フロントエンド
- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts (グラフ)

### データソース
- YouTube Data API
- Google News RSS
- Google Trends (pytrends)

## セットアップ

### 1. YouTube API キーの取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成
3. YouTube Data API v3 を有効化
4. 認証情報から API キーを作成

### 2. バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env ファイルを編集して YOUTUBE_API_KEY を設定

# サーバー起動
uvicorn app.main:app --reload
```

バックエンドは http://localhost:8000 で起動します。

### 3. フロントエンドのセットアップ

```bash
# 公開アプリ（ポート3000）
cd frontend
npm install
npm run dev

# 管理画面（ポート3001）- 別ターミナルで
cd frontend-admin
npm install
npm run dev
```

| アプリ | URL | 用途 |
|--------|-----|------|
| 公開アプリ | http://localhost:3000 | 一般ユーザー向け（閲覧のみ） |
| 管理画面 | http://localhost:3001 | 開発者向け（登録・ジョブ実行） |

## 使い方

### 基本的な流れ

1. **管理画面でチャンネルを追加**: http://localhost:3001/channels
2. **データ収集を実行**: http://localhost:3001/jobs で「データ収集」ボタン
3. **予測を実行**: 同じくジョブページで「予測実行」ボタン
4. **結果確認**: http://localhost:3000 でランキングを確認

### コマンドラインからの実行（任意）

```bash
cd backend

# データ収集
python scripts/collect_data.py

# 予測実行
python scripts/run_prediction.py

# モデル学習（6ヶ月分のデータが溜まったら）
python scripts/train_model.py
```

### 運用の流れ

| フェーズ | やること | 頻度 |
|---------|---------|------|
| 初期 | チャンネル追加 → データ収集 → 予測実行 | 1回 |
| 運用 | データ収集 → 予測実行 | 毎日〜週1 |
| 学習 | モデル学習（6ヶ月後） | 月1回程度 |

## 機械学習モデル

### 使用する特徴量

| 特徴量 | 説明 |
|--------|------|
| subscriber_count | 現在の登録者数 |
| subscriber_growth_rate_30d | 直近30日の登録者成長率 |
| subscriber_growth_rate_90d | 直近90日の登録者成長率 |
| view_count | 総再生回数 |
| view_growth_rate_30d | 直近30日の再生数成長率 |
| upload_frequency | 週あたりの投稿頻度 |
| engagement_rate | エンゲージメント率 |
| trend_score | Google Trendsスコア |
| news_count | ニュース記事数 |
| news_sentiment | ニュースのポジティブ/ネガティブ比率 |

### モデル

- LightGBM (Gradient Boosting)
- 回帰問題として半年後の成長率を予測

## API エンドポイント

### 公開API

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /api/ranking | 成長予測ランキング |
| GET | /api/channels | チャンネル一覧 |
| GET | /api/channels/{id} | チャンネル詳細 |
| GET | /api/news | ニュース一覧 |

### 管理API

| メソッド | パス | 説明 |
|---------|------|------|
| POST | /api/channels | チャンネル追加 |
| DELETE | /api/channels/{id} | チャンネル削除 |
| GET | /api/search/youtube | YouTube検索 |
| POST | /api/admin/collect | データ収集実行 |
| POST | /api/admin/predict | 予測実行 |
| POST | /api/admin/train | モデル学習 |

## 今後の課題

- [ ] 定期的なデータ収集ジョブの実装（GitHub Actions等）
- [ ] より多くの特徴量の追加
- [ ] 予測精度の検証・改善
- [ ] 認証機能の追加（管理画面）
