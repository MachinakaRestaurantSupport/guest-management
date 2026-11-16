## Context

顧客管理（guest-management）は MachinakaRestaurantSupportTools において、来客時の座席状況・来店セッション・清掃後の再利用可否および会員ポイントを一元管理するマイクロサービスである。初期MVPでは外部DBに依存しない高速なインメモリストアと FastAPI による REST API を提供する。

## Goals / Non-Goals

### Goals
- USDM 要求 `GuestManagement_R01` および下位仕様 `GuestManagement_R01.DM01-01`〜`04` を満たす REST API を提供する。
- 座席状態遷移（`available` → `occupied` → `cleaning` → `available`）の整合性を保証し、不正遷移時に HTTP 409 を返却する。
- 定員超過およびポイント残高不足時に HTTP 422 を返却する。

### Non-Goals
- 永続化データベース（PostgreSQL/SQLite等）の導入（MVP後の拡張対象）。
- 認証・認可基盤および他サービスとの実通信（結合試験は `system-integration` 側で管理）。

## Decisions

1. **Web フレームワーク**: FastAPI + Pydantic v2 を採用し、`create_app()` ファクトリ関数とモジュールレベルの `app = create_app()` を提供する。
2. **データストア**: スレッドセーフ性を意識したシンプルなインメモリ辞書ストア（`InMemoryStore`）を `store.py` に実装し、UUID4ベースの識別子およびトークンを生成する。
3. **エラーハンドリング**:
   - 未登録リソース: `404 Not Found`
   - 不正な状態遷移（例: `occupied` への二重着席、`available` への清掃要求、`occupied` への解放）: `409 Conflict`
   - 業務バリデーションエラー（`party_size > capacity`、ポイント残高不足）: `422 Unprocessable Content`

## USDM トレーサビリティ

| USDM 要求ID | 要件概要 | 対応エンドポイント / モジュール |
| --- | --- | --- |
| `GuestManagement_R01.DM01-01` | 座席登録・状態参照 | `POST /tables`, `GET /tables`, `GET /tables/{table_id}` (`main.py`, `store.py`, `models.py`) |
| `GuestManagement_R01.DM01-02` | 空席の着席遷移・来店セッションIDとQRトークン発行 | `POST /tables/{table_id}/occupy` (`main.py`, `store.py`) |
| `GuestManagement_R01.DM01-03` | 会計後の清掃要求および清掃完了による再利用可否制御 | `POST /tables/{table_id}/request-cleaning`, `POST /tables/{table_id}/release` (`main.py`, `store.py`) |
| `GuestManagement_R01.DM01-04` | 会員情報とポイントの管理 | `POST /guests`, `POST /guests/{guest_id}/points` (`main.py`, `store.py`, `models.py`) |

## Risks / Trade-offs

- インメモリ保持のためプロセス再起動でデータは初期化される（MVPフェーズの仕様として許容）。
