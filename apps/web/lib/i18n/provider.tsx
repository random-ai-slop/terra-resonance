'use client';
import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { resolveLocale, translate, type Locale, type Translator } from './core';
const STORAGE_KEY = 'terra.locale.v1';
const Context = createContext<{
  locale: Locale;
  t: Translator;
  setLocale: (locale: Locale) => void;
} | null>(null);
export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, updateLocale] = useState<Locale>('en');
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const restore = () => {
      let saved = null;
      try {
        saved = localStorage.getItem(STORAGE_KEY);
      } catch {
        /* Session preference still works. */
      }
      updateLocale(
        resolveLocale(new URL(location.href).searchParams.get('lang'), saved),
      );
      setReady(true);
    };
    restore();
    window.addEventListener('popstate', restore);
    return () => window.removeEventListener('popstate', restore);
  }, []);
  useEffect(() => {
    document.documentElement.lang = locale;
    document.title =
      locale === 'en'
        ? 'Terra Resonance · Earth normal modes'
        : 'Terra Resonance · 地球自由振荡';
    document
      .querySelector('meta[name="description"]')
      ?.setAttribute(
        'content',
        locale === 'en'
          ? 'Explore planetary normal modes through eigenfunctions, interior structure and material motion.'
          : '通过真实本征函数、内部结构与物质点运动，探索球对称行星的自由振荡。',
      );
  }, [locale]);
  const value = useMemo(
    () => ({
      locale,
      t: ((key, params) => translate(locale, key, params)) as Translator,
      setLocale(next: Locale) {
        updateLocale(next);
        try {
          localStorage.setItem(STORAGE_KEY, next);
        } catch {
          /* No persistence permission is needed to switch. */
        }
        const url = new URL(location.href);
        url.searchParams.set('lang', next);
        history.replaceState(history.state, '', url);
      },
    }),
    [locale],
  );
  return (
    <Context.Provider value={value}>
      {ready ? (
        children
      ) : (
        <main className="loading">
          <h1>Terra Resonance</h1>
        </main>
      )}
    </Context.Provider>
  );
}
export function useLocale() {
  const value = useContext(Context);
  if (!value) throw new Error('LocaleProvider is required');
  return value;
}
