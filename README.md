# Blue One

[English](README.md) | [Japanese](README.ja.md)

Translate text, PDFs, Word, Excel, PowerPoint, and images from Claude or Codex. The plugin includes the Blue One MCP connection and a skill that handles file transfers, progress, results, and troubleshooting.

A Blue One account is required; normal translation charges apply.

## Claude Code or Codex

Paste this into your coding agent:

```text
Install the Blue One translation plugin from https://github.com/yellowblue1/blue-one-plugin for my user account in this coding agent. Read README.md and inspect the plugin manifests first. Use the installed CLI's supported plugin commands; check --help if needed. Register the GitHub marketplace, install blue-one@blue-one, and verify that the skill and remote MCP server are present. Keep existing settings and other plugins. If GitHub access, OAuth sign-in, a restart, or administrator approval is required, explain the exact next step and wait for me. Do not start a translation, buy credits, or change organization policies. Report installation and authentication separately.
```

Or install from your terminal:

| Claude Code | Codex |
| --- | --- |
| `claude plugin marketplace add yellowblue1/blue-one-plugin` | `codex plugin marketplace add yellowblue1/blue-one-plugin` |
| `claude plugin install blue-one@blue-one` | `codex plugin add blue-one@blue-one` |

Start a new session after installation and complete the host's Blue One sign-in flow. If your CLI has no plugin commands, update it or use its plugin settings. A coding agent can install the package; sign-in and organization approval can require your action.

## Claude chat / Cowork

In **Customize → Plugins → Add → Add marketplace**, enter:

```text
https://github.com/yellowblue1/blue-one-plugin
```

Add **Blue One**, open its **Connectors** tab, and add/connect Blue One. Sign in and select your team.

## Use

Ask: "Translate this PowerPoint into English while preserving its layout."

The plugin uses Blue One's actual translation result. If a step fails, it explains the next action instead of silently rebuilding the document or repeating a billable translation.

## Requirements

- File transfers use Python 3.9+ in the agent's execution environment. No build step, mise, or dependency installation is needed.
- On Claude Team/Enterprise, an owner may need to allow the plugin source, add the connector, and allow file-execution network access to **mcp.blue1.app**. Each member completes OAuth.
- Installation and OAuth are separate. Organization policies and network restrictions still apply.

No redistribution license is currently specified.
