import { strToU8, zipSync } from 'fflate';
import { download } from './data';

/** Keep the scientific artifact and its provenance inseparable at download.
 * Browsers may block a second automatic download from the same click. */
export async function downloadArtifact(
  name: string,
  data: Blob | string | Uint8Array,
  metadata: unknown,
): Promise<void> {
  const bytes =
    typeof data === 'string'
      ? strToU8(data)
      : data instanceof Blob
        ? new Uint8Array(await data.arrayBuffer())
        : data;
  const zip = zipSync(
    {
      [name]: bytes,
      [`${name}.json`]: strToU8(JSON.stringify(metadata, null, 2)),
    },
    { level: 0 },
  );
  download(
    `${name}.zip`,
    new Blob([new Uint8Array(zip)], { type: 'application/zip' }),
  );
}
