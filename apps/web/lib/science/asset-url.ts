/** Build-time deployment prefix; user imports and downloads stay local. */
export function assetUrl(path: string): string {
  return `${process.env.NEXT_PUBLIC_BASE_PATH ?? ''}/${path.replace(/^\/+/, '')}`;
}
