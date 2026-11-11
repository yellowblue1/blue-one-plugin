# Blue One

[English](README.md) | [日本語](README.ja.md)

ClaudeやCodexから、文章・PDF・Word・Excel・PowerPoint・画像を翻訳できます。Blue OneのMCP接続と、ファイル転送・進捗確認・結果取得・トラブル対応を行うスキルをまとめたプラグインです。

**非公開プレビュー：** リポジトリへのアクセス権が必要です。Blue Oneのアカウントと、通常の翻訳料金が必要です。

## Claude Code・Codex

次のプロンプトを貼り付けてください。

```text
Install the Blue One translation plugin from https://github.com/yellowblue1/blue-one-plugin for my user account in this coding agent. Read README.md and inspect the plugin manifests first. Use the installed CLI's supported plugin commands; check --help if needed. Register the GitHub marketplace, install blue-one@blue-one, and verify that the skill and remote MCP server are present. Keep existing settings and other plugins. If GitHub access, OAuth sign-in, a restart, or administrator approval is required, explain the exact next step and wait for me. Do not start a translation, buy credits, or change organization policies. Report installation and authentication separately.
```

ターミナルから直接インストールすることもできます。

| Claude Code | Codex |
| --- | --- |
| `claude plugin marketplace add yellowblue1/blue-one-plugin` | `codex plugin marketplace add yellowblue1/blue-one-plugin` |
| `claude plugin install blue-one@blue-one` | `codex plugin add blue-one@blue-one` |

インストール後に新しいセッションを開き、利用するホストの案内に従ってBlue Oneにログインします。CLIにプラグインのコマンドがない場合は、更新するかプラグインの設定画面を使ってください。AIがインストールを進められても、ログインや組織の承認には本人の操作が必要な場合があります。

## Claude chat・Cowork

**Customize → Plugins → Add → Add marketplace**で、次のURLを入力します。

```text
https://github.com/yellowblue1/blue-one-plugin
```

**Blue One**を追加し、**Connectors**タブでBlue Oneを追加・接続します。ログインしてチームを選んでください。非公開プレビューの間は、ClaudeにもこのリポジトリへのGitHubアクセス権が必要です。

## 使い方

例えば「このパワーポイントを英訳して、レイアウトを保ってください」と依頼します。

Blue Oneで実際に翻訳した結果を返します。途中で失敗した場合は、独自の資料再構築や課金される翻訳の繰り返しを自動で行わず、次に必要な操作を案内します。

## 必要な設定

- ファイル転送には、AIの実行環境にPython 3.9以上が必要です。ビルド・mise・依存パッケージのインストールは不要です。
- Claude Team・Enterpriseでは、オーナーによるプラグイン配布元の許可、コネクタの追加、ファイル実行環境から**mcp.blue1.app**への通信許可が必要な場合があります。OAuth認証は各メンバーが行います。
- インストールとOAuth認証は別です。組織のポリシーや通信制限は引き続き適用されます。

このプレビューの再配布ライセンスは未確定です。
