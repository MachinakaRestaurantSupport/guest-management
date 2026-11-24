# table-lifecycle Specification

## Purpose
顧客管理（guest-management）における座席ライフサイクル管理、来店セッション・QRトークン発行、および会員ポイント管理のAPI仕様を定義する。

## Requirements

### Requirement: Table lifecycle management
システムは座席登録・状態遷移・会員ポイントを管理しなければならない（MUST）。

#### Scenario: Occupy available table
- **WHEN** `available` な座席に `POST /tables/{table_id}/occupy` を実行した場合
- **THEN** `occupied` へ遷移しセッションIDとQRトークンを発行する（SHALL）

#### Scenario: Invalid state transition
- **WHEN** 不正な状態の座席に遷移APIを実行した場合
- **THEN** HTTP 409 を返却する（MUST）

#### Scenario: Capacity exceeded or insufficient points
- **WHEN** 定員超過またはポイント残高不足が発生した場合
- **THEN** HTTP 422 を返却する（MUST）

### Requirement: サブモジュール参照のコミット指定管理

本リポジトリは `.gitmodules` に `branch` 設定を持たせず `reference/system-integration` を確定コミット SHA（gitlink）指定で管理しなければならず（MUST）、`reference/system-integration/` 配下を読み取り専用として直接変更してはならない（SHALL）。

#### Scenario: サブモジュール参照の更新とマージ

- **WHEN** `system-integration` の確定コミット SHA（`<commit-sha>`）を `reference/system-integration` にチェックアウトし、`system-integration` PR の Merge commit マージ後に本リポジトリの PR を `main` にマージするとき
- **THEN** `.gitmodules` の書き換えやマージ後の `main` 戻し作業なしで、正しい仕様・画像参照を維持したままマージが完了する（SHALL）
