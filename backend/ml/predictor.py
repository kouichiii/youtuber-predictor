import os
import pickle
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


class GrowthPredictor:
    """YouTuberの成長予測を行うLightGBMモデル"""

    FEATURE_COLUMNS = [
        "subscriber_count",
        "subscriber_growth_rate_30d",
        "subscriber_growth_rate_90d",
        "view_count",
        "view_growth_rate_30d",
        "video_count",
        "upload_frequency",
        "avg_views_per_video",
        "engagement_rate",
        "trend_score",
        "trend_direction",
        "trend_volatility",
        "news_count",
        "news_positive_ratio",
        "news_negative_ratio",
        "channel_age_days",
    ]

    def __init__(self, model_path: str = "ml/model.pkl"):
        self.model_path = model_path
        self.model: Optional[lgb.Booster] = None
        self._load_model()

    def _load_model(self):
        """保存されたモデルを読み込み"""
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)

    def save_model(self):
        """モデルを保存"""
        if self.model:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)

    def prepare_features(self, channel_data: Dict[str, Any]) -> np.ndarray:
        """
        チャンネルデータから特徴量を準備

        Args:
            channel_data: チャンネルの各種データ
        """
        features = []

        for col in self.FEATURE_COLUMNS:
            value = channel_data.get(col, 0)
            if value is None:
                value = 0
            features.append(float(value))

        return np.array(features).reshape(1, -1)

    def predict(self, channel_data: Dict[str, Any]) -> Dict[str, float]:
        """
        半年後の成長率を予測

        Args:
            channel_data: チャンネルの各種データ

        Returns:
            予測結果（成長率、信頼度）
        """
        if self.model is None:
            # モデルがない場合はルールベースで予測
            return self._rule_based_prediction(channel_data)

        features = self.prepare_features(channel_data)
        prediction = self.model.predict(features)[0]

        # 信頼度の計算（特徴量の欠損が少ないほど高い）
        non_null_count = sum(1 for col in self.FEATURE_COLUMNS if channel_data.get(col) is not None)
        confidence = non_null_count / len(self.FEATURE_COLUMNS)

        return {
            "predicted_growth_rate": float(prediction),
            "confidence_score": float(confidence)
        }

    def _rule_based_prediction(self, channel_data: Dict[str, Any]) -> Dict[str, float]:
        """
        モデルがない場合のルールベース予測

        直近の成長率とトレンドスコアを基に予測
        """
        # 直近の成長率（30日）を基準に
        growth_30d = channel_data.get("subscriber_growth_rate_30d", 0) or 0
        growth_90d = channel_data.get("subscriber_growth_rate_90d", 0) or 0

        # トレンドスコアによる調整
        trend_score = channel_data.get("trend_score", 50) or 50
        trend_factor = (trend_score - 50) / 100  # -0.5 ~ 0.5

        # ニュース数による調整
        news_count = channel_data.get("news_count", 0) or 0
        news_factor = min(news_count * 0.01, 0.1)  # 最大10%上乗せ

        # 投稿頻度による調整
        upload_frequency = channel_data.get("upload_frequency", 0) or 0
        upload_factor = min(upload_frequency * 0.5, 0.1)  # 定期投稿で上乗せ

        # 半年後の成長率を推定（月次成長率 × 6 + 調整）
        base_growth = (growth_30d + growth_90d / 3) / 2 * 6
        adjusted_growth = base_growth * (1 + trend_factor) + news_factor + upload_factor

        # 信頼度（ルールベースは低め）
        non_null_count = sum(1 for col in self.FEATURE_COLUMNS if channel_data.get(col) is not None)
        confidence = (non_null_count / len(self.FEATURE_COLUMNS)) * 0.7  # ルールベースなので70%に抑える

        return {
            "predicted_growth_rate": float(adjusted_growth),
            "confidence_score": float(confidence)
        }

    def train(self, training_data: pd.DataFrame, target_column: str = "actual_growth_rate"):
        """
        モデルを学習

        Args:
            training_data: 学習データ（特徴量 + 正解ラベル）
            target_column: 正解ラベルのカラム名
        """
        # 特徴量とターゲットを分離
        X = training_data[self.FEATURE_COLUMNS]
        y = training_data[target_column]

        # 欠損値を0で埋める
        X = X.fillna(0)

        # 学習データと検証データに分割
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        # LightGBMのデータセット
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)

        # パラメータ
        params = {
            "objective": "regression",
            "metric": "rmse",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
        }

        # 学習
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=1000,
            valid_sets=[train_data, val_data],
            callbacks=[lgb.early_stopping(stopping_rounds=50)]
        )

        # 評価
        y_pred = self.model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        r2 = r2_score(y_val, y_pred)

        print(f"Validation RMSE: {rmse:.4f}")
        print(f"Validation R2: {r2:.4f}")

        # モデルを保存
        self.save_model()

        return {"rmse": rmse, "r2": r2}

    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量の重要度を取得"""
        if self.model is None:
            return {}

        importance = self.model.feature_importance(importance_type="gain")
        return dict(zip(self.FEATURE_COLUMNS, importance))
