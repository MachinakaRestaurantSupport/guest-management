## Purpose

顧客管理（guest-management）における座席ライフサイクル管理、来店セッション・QRトークン発行、および会員ポイント管理のAPI仕様を定義する。

## ADDED Requirements

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
