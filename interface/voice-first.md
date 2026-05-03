# Voice-First Interface

PFO must accept natural language, voice transcripts, and short commands as equivalent input.

## Input Contract

The interface should normalize short requests into an execution intent.

Examples:

```text
сделай SaaS для учета подписок
```

```text
Telegram бот для продаж с CRM и уведомлениями
```

```text
CLI для массовой проверки ссылок
```

## Output Contract

After each stage, return operational state:

```text
CURRENT STATE:
GENERATED ARTIFACT:
VALIDATION STATUS:
NEXT ACTION:
```

Conversational explanation is allowed only when it clarifies a blocking decision or asks a necessary question.

