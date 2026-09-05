import { messages, type MessageKey } from './messages';
export type Locale = 'en' | 'zh-CN';
export type MessageValue = string | number | boolean | null | TextToken;
export type TextToken = {
  key: MessageKey;
  params: Record<string, MessageValue>;
};
export type Translator = (
  key: MessageKey,
  params?: Record<string, MessageValue>,
) => string;
export function isLocale(value: unknown): value is Locale {
  return value === 'en' || value === 'zh-CN';
}
export function resolveLocale(
  query: string | null,
  saved: string | null,
): Locale {
  return isLocale(query) ? query : isLocale(saved) ? saved : 'en';
}
export function message(
  key: MessageKey,
  params: Record<string, MessageValue> = {},
): TextToken {
  return { key, params };
}
export function translate(
  locale: Locale,
  key: MessageKey,
  params: Record<string, MessageValue> = {},
): string {
  const template = locale === 'zh-CN' ? messages[key] : key;
  return template.replace(/\{(\w+)\}/g, (_, name: string) => {
    if (!(name in params))
      throw new Error(`Missing message parameter: ${name}`);
    const value = params[name];
    return value !== null && typeof value === 'object'
      ? translate(locale, value.key, value.params)
      : String(value ?? '');
  });
}
export function formatMessage(locale: Locale, token: TextToken): string {
  return translate(locale, token.key, token.params);
}
/** Canonical English diagnostics carry a stable identity across async/UI boundaries. */
export class DiagnosticError extends Error {
  readonly diagnostic: TextToken;
  constructor(key: MessageKey, params: Record<string, MessageValue> = {}) {
    super(translate('en', key, params));
    this.name = 'DiagnosticError';
    this.diagnostic = message(key, params);
  }
}
export function issue(
  key: MessageKey,
  params: Record<string, MessageValue> = {},
) {
  return new DiagnosticError(key, params);
}
export function formatError(locale: Locale, error: unknown): string {
  if (!error) return '';
  if (error instanceof ContextualError)
    return `${formatMessage(locale, error.context)} ${formatError(locale, error.cause)}`;
  if (error instanceof DiagnosticError)
    return formatMessage(locale, error.diagnostic);
  let detail: string;
  try {
    detail =
      error instanceof Error
        ? error.message
        : typeof error === 'string'
          ? error
          : (JSON.stringify(error) ?? 'Unknown diagnostic');
  } catch {
    detail = 'Unserializable diagnostic';
  }
  return locale === 'en'
    ? detail
    : translate(locale, 'The operation could not be completed: {detail}', {
        detail,
      });
}

export class ContextualError extends Error {
  constructor(
    readonly context: TextToken,
    override readonly cause: unknown,
  ) {
    super(`${formatMessage('en', context)} ${formatError('en', cause)}`);
  }
}
