# guest-management

来客時の注文受付開始（座席QRトークン発行）、席の使用状況（空席・着席中・清掃中）、会員ポイント付与および会計後の席の再利用可否を管理するツールです。  
店長・スタッフ共通ポータル（[ポータル画面イメージ](reference/system-integration/docs/images/portal/01-portal-dashboard.png)）のフロア運用を支え、店内注文および会計管理と I-6 契約で連携します。

## 画面遷移図

縮小画面キャプチャを用いた `guest-management` の画面遷移図です（draw.io 編集用ソース: [transition.drawio](reference/system-integration/docs/images/guest_management/transition.drawio)）。

![guest-management 画面遷移図](reference/system-integration/docs/images/guest_management/transition.svg)

## 代表機能イメージ

### 1. 座席ステータスマップ (`GET /ui/tables`)
店舗内の全テーブルについて、`available`（空席・案内可）・`occupied`（着席中）・`cleaning`（清掃中）の3状態をリアルタイムに俯瞰し、次のアクション（着席受付／清掃完了）へ遷移できます。

![座席ステータスマップ](reference/system-integration/docs/images/guest_management/01-table-map.png)

### 2. 来客受付・QRコード発行 (`GET /ui/checkin`)
空席を選択して来店人数の定員検証を行い、着席セッション開始（`POST /tables/{table_id}/occupy`）と同時に店内注文用QRトークンを発行します。

![来客受付・QR発行](reference/system-integration/docs/images/guest_management/02-table-checkin-qr.png)

### 3. 会員ポイント管理・席清掃完了 (`GET /ui/guests`)
会員顧客のポイント加算・参照と、会計完了後に清掃中となった座席の清掃完了操作（`POST /tables/{table_id}/release`）による空席復帰を行います。

![会員ポイント・席清掃完了](reference/system-integration/docs/images/guest_management/03-guest-loyalty.png)

## 提供 API・UI エンドポイント

| 種別 | メソッド & パス | 機能概要 |
|---|---|---|
| API | `GET /health` | ヘルスチェック |
| API | `POST /tables` / `GET /tables` / `GET /tables/{table_id}` | 座席の登録・一覧・詳細取得 |
| API | `POST /tables/{table_id}/occupy` | 来客受付・着席・QRトークン発行 |
| API | `POST /tables/{table_id}/request-cleaning` | 会計後の清掃中ステータス遷移 |
| API | `POST /tables/{table_id}/release` | 清掃完了・空席への再利用復帰 |
| API | `POST /guests` / `POST /guests/{guest_id}/points` | 会員登録・ポイント残高調整 |
| UI | `GET /ui/tables` | 座席ステータスマップ画面 |
| UI | `GET /ui/checkin` | 来客受付・QR発行画面 |
| UI | `GET /ui/guests` | 会員ポイント・席清掃完了画面 |

## テスト・静的解析の実行

```bash
../.venv/bin/python3 -m pytest -v
../.venv/bin/ruff check .
```
