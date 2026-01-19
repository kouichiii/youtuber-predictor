"use client";

import { useState } from "react";
import { runDataCollection, runPrediction, runTraining } from "@/lib/api";

interface JobLog {
  timestamp: string;
  type: "info" | "success" | "error";
  message: string;
}

export default function JobsPage() {
  const [logs, setLogs] = useState<JobLog[]>([]);
  const [runningJob, setRunningJob] = useState<string | null>(null);

  const addLog = (type: JobLog["type"], message: string) => {
    setLogs((prev) => [
      ...prev,
      {
        timestamp: new Date().toLocaleTimeString("ja-JP"),
        type,
        message,
      },
    ]);
  };

  const handleRunJob = async (
    jobName: string,
    jobFn: () => Promise<{ message: string }>
  ) => {
    if (runningJob) {
      alert("別のジョブが実行中です");
      return;
    }

    setRunningJob(jobName);
    addLog("info", `${jobName} を開始しました...`);

    try {
      const result = await jobFn();
      addLog("success", result.message);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || "エラーが発生しました";
      addLog("error", `${jobName} 失敗: ${errorMessage}`);
    } finally {
      setRunningJob(null);
    }
  };

  const jobs = [
    {
      id: "collect",
      name: "データ収集",
      description:
        "YouTube/Google News/Google Trendsからデータを収集してDBに保存します",
      fn: runDataCollection,
      color: "blue",
    },
    {
      id: "predict",
      name: "予測実行",
      description: "DBのデータを使って全チャンネルの成長予測を実行します",
      fn: runPrediction,
      color: "green",
    },
    {
      id: "train",
      name: "モデル学習",
      description:
        "6ヶ月分の履歴データを使ってモデルを学習します（データが必要）",
      fn: runTraining,
      color: "purple",
    },
  ];

  const getLogStyle = (type: JobLog["type"]) => {
    switch (type) {
      case "success":
        return "text-green-600";
      case "error":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">ジョブ実行</h1>

      {/* Job Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {jobs.map((job) => (
          <div key={job.id} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-2">{job.name}</h3>
            <p className="text-gray-500 text-sm mb-4">{job.description}</p>
            <button
              onClick={() => handleRunJob(job.name, job.fn)}
              disabled={runningJob !== null}
              className={`w-full py-2 rounded-lg font-medium transition-colors ${
                runningJob === job.name
                  ? "bg-gray-200 text-gray-500 cursor-wait"
                  : runningJob !== null
                  ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                  : `bg-${job.color}-600 text-white hover:bg-${job.color}-700`
              }`}
              style={{
                backgroundColor:
                  runningJob === null
                    ? job.color === "blue"
                      ? "#2563eb"
                      : job.color === "green"
                      ? "#16a34a"
                      : "#9333ea"
                    : undefined,
              }}
            >
              {runningJob === job.name ? "実行中..." : "実行"}
            </button>
          </div>
        ))}
      </div>

      {/* Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">実行ログ</h2>
          {logs.length > 0 && (
            <button
              onClick={() => setLogs([])}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              クリア
            </button>
          )}
        </div>

        {logs.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            ログはまだありません
          </div>
        ) : (
          <div className="space-y-2 font-mono text-sm max-h-96 overflow-y-auto">
            {logs.map((log, index) => (
              <div key={index} className={`${getLogStyle(log.type)}`}>
                <span className="text-gray-400">[{log.timestamp}]</span>{" "}
                {log.message}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-yellow-800 mb-2">使い方</h3>
        <ol className="text-sm text-yellow-700 space-y-1 list-decimal list-inside">
          <li>まず「チャンネル管理」からYouTuberを追加してください</li>
          <li>「データ収集」を実行してデータをDBに保存します</li>
          <li>「予測実行」で成長予測を計算します</li>
          <li>6ヶ月分のデータが溜まったら「モデル学習」を実行できます</li>
        </ol>
      </div>
    </div>
  );
}
