## 0. 初期セットアップ

- [x] 0.1 初期ファイル・submodule・`.gitignore` のコミット
- [x] 0.2 OpenSpec `init` 変更の作成と検証

## 1. プロジェクト基盤

- [x] 1.1 `pyproject.toml`（`name="guest-management"`, pytest/ruff 設定）の追加

## 2. アプリケーション実装

- [x] 2.1 ドメインモデル（`src/guest_management/__init__.py`, `models.py`）の実装 [GuestManagement_R01.DM01-01, GuestManagement_R01.DM01-04]
- [ ] 2.2 インメモリストア（`src/guest_management/store.py`）の実装 [GuestManagement_R01.DM01-01, GuestManagement_R01.DM01-02, GuestManagement_R01.DM01-03, GuestManagement_R01.DM01-04]
- [ ] 2.3 FastAPI エンドポイント（`src/guest_management/main.py`）の実装 [GuestManagement_R01.DM01-01, GuestManagement_R01.DM01-02, GuestManagement_R01.DM01-03, GuestManagement_R01.DM01-04]

## 3. 検証・品質確認

- [ ] 3.1 単体試験（`tests/test_guests_and_tables.py`）の作成と `pytest` 全パス確認
- [ ] 3.2 `ruff check` / `ruff format` による品質確認
