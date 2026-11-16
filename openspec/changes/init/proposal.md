## Why

店舗運営において、着席前の不正注文や清掃未完了席への誤案内を防止し、座席の回転率と顧客体験を向上させるため、顧客管理（guest-management）サービスの初期MVPを構築する。

## What Changes

- 座席（Table）の登録・一覧・詳細取得および状態遷移（`available` → `occupied` → `cleaning` → `available`）を提供するAPIを追加する。
- 着席時に来店セッションIDとQRトークンを発行し、不正な状態遷移（409）および定員超過（422）を検証する。
- 会員（Guest）の登録およびポイント加減算API（残高不足時は422）を追加する。
- FastAPIベースのインメモリストア実装と単体試験を追加する。

## Capabilities

### New Capabilities

- `table-lifecycle`: 座席ライフサイクル管理（登録・着席・清掃要求・解放）および会員ポイント管理機能。

### Modified Capabilities

なし（新規リポジトリの初期実装）。

## Impact

- `pyproject.toml`: Pythonパッケージ設定・pytest/ruff設定を追加。
- `src/guest_management/`: FastAPIアプリケーション、Pydanticモデル、インメモリストアを追加。
- `tests/test_guests_and_tables.py`: 全エンドポイントおよび異常系（404/409/422）の単体試験を追加。
- `reference/system-integration/`: 読み取り専用参照のみであり変更なし。
