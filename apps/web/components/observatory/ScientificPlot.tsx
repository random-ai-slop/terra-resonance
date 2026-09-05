import {
  translate,
  type Locale,
  type Translator,
  type TextToken,
} from '@/lib/i18n/core';
import { tickLabel } from '@/lib/science/chart-data';
export type PlotLabel = string | TextToken;
export function labelText(locale: Locale, label: PlotLabel): string {
  return typeof label === 'string'
    ? label
    : translate(locale, label.key, label.params);
}
export type Series = { name: PlotLabel; color: string; points: number[][] };
export default function ScientificPlot({
  locale,
  series,
  xlabel,
  ylabel,
  cursor,
}: {
  locale: Locale;
  series: Series[];
  xlabel: PlotLabel;
  ylabel: PlotLabel;
  cursor?: number;
}) {
  const tr: Translator = (key, params) => translate(locale, key, params);
  const x = labelText(locale, xlabel),
    y = labelText(locale, ylabel);
  const xEn = labelText('en', xlabel),
    yEn = labelText('en', ylabel);
  const legends = Array.from(
    new Map(series.map((s) => [labelText('en', s.name), s])).values(),
  );
  const points = series.flatMap((s) => s.points),
    xs = points.map((p) => p[0]),
    ys = points.map((p) => p[1]);
  let xmin = Infinity,
    xmax = -Infinity,
    ymin = Infinity,
    ymax = -Infinity;
  for (const x of xs) {
    xmin = Math.min(xmin, x);
    xmax = Math.max(xmax, x);
  }
  for (const y of ys) {
    ymin = Math.min(ymin, y);
    ymax = Math.max(ymax, y);
  }
  if (!points.length) return <p>{tr('No data to plot.')}</p>;
  if (xmin === xmax) xmax = xmin + 1;
  if (ymin === ymax) {
    ymin -= 1;
    ymax += 1;
  }
  const pad = (ymax - ymin) * 0.08;
  ymin -= pad;
  ymax += pad;
  const X = (v: number) => 64 + ((v - xmin) / (xmax - xmin)) * 680,
    Y = (v: number) => 205 - ((v - ymin) / (ymax - ymin)) * 168;
  return (
    <div className="plot-wrap">
      {/* An inline SVG with a title is an accessible graphic, not an HTML img. */}
      <svg
        viewBox={`0 0 790 ${254 + Math.ceil(legends.length / 5) * 22}`}
        // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role -- SVG graphics use role=img with a title.
        role="img"
        aria-label={tr('{p0} versus {p1}', { p0: y, p1: x })}
        data-export-aria-label={`${yEn} versus ${xEn}`}
      >
        <title data-export-text={`${yEn} versus ${xEn}`}>
          {tr('{p0} versus {p1}', { p0: y, p1: x })}
        </title>
        {[0, 0.25, 0.5, 0.75, 1].map((k) => (
          <g key={k}>
            <line
              x1="64"
              x2="744"
              y1={205 - k * 168}
              y2={205 - k * 168}
              stroke="currentColor"
              opacity=".1"
            />
            <text x="54" y={209 - k * 168} textAnchor="end">
              {tickLabel(ymin + k * (ymax - ymin), (ymax - ymin) / 4)}
            </text>
            <text x={64 + k * 680} y="225" textAnchor="middle">
              {tickLabel(xmin + k * (xmax - xmin), (xmax - xmin) / 4)}
            </text>
          </g>
        ))}
        <line
          x1="64"
          x2="744"
          y1="205"
          y2="205"
          stroke="currentColor"
          opacity=".3"
        />
        {series.map((s, i) => (
          <path
            key={i}
            d={s.points
              .map(
                (p, j) =>
                  `${j ? 'L' : 'M'}${X(p[0]).toFixed(2)},${Y(p[1]).toFixed(2)}`,
              )
              .join(' ')}
            stroke={s.color}
            fill="none"
            strokeWidth="1.8"
          />
        ))}
        {cursor !== undefined && cursor >= xmin && cursor <= xmax && (
          <line
            x1={X(cursor)}
            x2={X(cursor)}
            y1="36"
            y2="205"
            stroke="currentColor"
            opacity=".6"
            strokeDasharray="3 4"
          />
        )}
        <text x="64" y="20" data-export-text={yEn}>
          {y}
        </text>
        <text x="744" y="246" textAnchor="end" data-export-text={xEn}>
          {x}
        </text>
        {Array.from(
          new Map(series.map((s) => [labelText('en', s.name), s])).values(),
        ).map((s, i) => (
          <g key={labelText('en', s.name)}>
            <line
              x1={64 + (i % 5) * 140}
              x2={80 + (i % 5) * 140}
              y1={266 + Math.floor(i / 5) * 22}
              y2={266 + Math.floor(i / 5) * 22}
              stroke={s.color}
              strokeWidth="2"
            />
            <text
              x={85 + (i % 5) * 140}
              y={270 + Math.floor(i / 5) * 22}
              data-export-text={labelText('en', s.name)}
            >
              {labelText(locale, s.name)}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
