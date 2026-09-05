import canonicalize from 'canonicalize';
import translations from './lessons-zh.json';
import type { Locale } from './core';
import type { Scene, ProbeSpec, ExportSpec } from '../science/types';
export type Lesson = {
  id: string;
  title: string;
  steps: string[];
  conclusion: string;
  caution: string;
  scene: Scene;
  probe?: ProbeSpec;
  export?: ExportSpec;
  [key: string]: unknown;
};
export type Lessons = { bundle_hash: string; lessons: Lesson[] };
export function lessonMetadata(lesson: Lesson) {
  const { scene: _scene, probe: _probe, export: _export, ...teaching } = lesson;
  return teaching;
}
export function recognizedLesson(
  bundleHash: string,
  teaching: unknown,
  catalog: Lessons | null,
): Lesson | null {
  if (
    !catalog ||
    catalog.bundle_hash !== bundleHash ||
    !teaching ||
    typeof teaching !== 'object'
  )
    return null;
  const lesson = catalog.lessons.find(
    (l) => l.id === (teaching as { id?: unknown }).id,
  );
  return lesson &&
    canonicalize(teaching) === canonicalize(lessonMetadata(lesson))
    ? lesson
    : null;
}
/** Call only for a canonical catalog lesson; never translate arbitrary project metadata. */
export function localizeLesson(lesson: Lesson, locale: Locale): Lesson {
  const text = translations[lesson.id as keyof typeof translations];
  return locale === 'zh-CN' && text ? { ...lesson, ...text } : lesson;
}
