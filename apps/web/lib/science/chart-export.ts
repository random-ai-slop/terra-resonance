/** Clone numeric geometry, replacing only explicitly owned annotation nodes.
 * English text comes from the same typed plot description as the visible labels.
 * Arbitrary user names are never searched or translated; no UI locale is changed.
 */
export function englishSvg(svg: SVGElement): string {
  const copy = svg.cloneNode(true) as SVGElement;
  copy.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  copy.setAttribute(
    'style',
    'color:#516b79;background:#f9fbfb;font-family:Arial,sans-serif;font-size:11px',
  );
  copy.setAttribute('lang', 'en');
  const title = copy.getAttribute('data-export-aria-label');
  if (title) copy.setAttribute('aria-label', title);
  copy.removeAttribute('data-export-aria-label');
  for (const node of copy.querySelectorAll('[data-export-text]')) {
    node.textContent = node.getAttribute('data-export-text');
    node.removeAttribute('data-export-text');
  }
  copy
    .querySelectorAll('text')
    .forEach((t) => t.setAttribute('fill', '#516b79'));
  return new XMLSerializer().serializeToString(copy);
}
