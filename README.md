# Reminder

Google SpreadsheetのデータをLINEに自動送信するGitHub Actions。

## 実行スケジュール

| ワークフロー | 実行タイミング | 対象シート | メッセージヘッダー |
|---|---|---|---|
| `daily.yml` | 毎日 07:00 JST | `Daily` | 【日次共有】 |
| `weekly.yml` | 毎週日曜 21:00 JST | `Weekly` | 【週次共有】 |
| `monthly.yml` | 毎月末日 09:00 JST | `Monthly` | 【月次共有】 |

## Spreadsheetの記載方法

スプレッドシートには `Monthly`、`Weekly`、`Daily` の3シートを用意する。

各シートはA列のみ使用：

| A列 |
|---|
| タイトル（ヘッダー行・送信されない） |
| 送信したい内容1 |
| 送信したい内容2 |
| ... |

- **1行目**はヘッダー行として扱われ、LINEには送信されない
- **2行目以降**がLINEに送信される
- 空行は無視される

**送信されるメッセージ例：**
```
【月次共有】
・売上レポート確認
・経費精算締め
```

## セットアップ

### 1. Google Sheets APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Google Sheets APIを有効化
3. サービスアカウントを作成し、JSONキーをダウンロード
4. スプレッドシートをサービスアカウントのメールアドレスに**閲覧者**として共有

### 2. LINE Messaging APIの設定

1. [LINE Developers](https://developers.line.biz/) でチャネルを作成（Messaging API）
2. チャネルアクセストークンを発行
3. ボットを自分のLINEに友達追加し、ユーザーIDを取得

### 3. GitHub Secretsの登録

```bash
gh secret set GOOGLE_SERVICE_ACCOUNT_JSON < service.json
gh secret set LINE_CHANNEL_ACCESS_TOKEN
gh secret set LINE_USER_ID
gh secret set SPREADSHEET_ID
```

> `LINE_CHANNEL_ACCESS_TOKEN`、`LINE_USER_ID`、`SPREADSHEET_ID` は対話形式で入力を求められる。

### 4. Secretsの確認

```bash
gh secret list
```

## ローカル実行（テスト）

```bash
pip install -r requirements.txt

export GOOGLE_SERVICE_ACCOUNT_JSON=$(cat service.json)
export LINE_CHANNEL_ACCESS_TOKEN=your_token
export LINE_USER_ID=your_user_id
export SPREADSHEET_ID=your_spreadsheet_id

python notify.py daily
python notify.py weekly
python notify.py monthly   # 末日以外はスキップされる
```

## 手動実行（GitHub Actions）

```bash
gh workflow run daily.yml
gh workflow run weekly.yml
gh workflow run monthly.yml
```

または GitHub の Actions タブ → 対象ワークフロー → **Run workflow** ボタン。

> `monthly.yml` の手動実行は末日以外だとスキップされる。テストしたい場合は `notify.py` の `is_last_day_of_month()` チェックを一時的にコメントアウトする。
