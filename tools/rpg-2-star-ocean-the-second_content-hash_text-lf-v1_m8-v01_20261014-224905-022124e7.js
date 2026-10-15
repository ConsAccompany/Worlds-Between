// Content-hash helpers shared by the Node checks. Mirrors the readiness builder
// (tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py).
//   sha256-bytes       SHA-256 of the exact file bytes. Binary files (PNG) only.
//   sha256-text-lf-v1  SHA-256 of the file bytes after each CRLF pair is replaced by LF. Text files (JSON, Markdown)
//                      only, so a lock reads the same in an LF checkout and in a core.autocrlf=true CRLF checkout.
//                      Nothing else is normalized (lone CR, BOM, whitespace, Unicode form stay as they are). Input
//                      with a NUL byte or invalid UTF-8 is refused instead of being hashed as text.
const crypto = require('node:crypto');

const BYTES_HASH = 'sha256-bytes';
const TEXT_HASH = 'sha256-text-lf-v1';

const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');

function textLfBytes(buffer) {
  if (buffer.includes(0)) throw new Error('NUL byte: not a text file');
  new TextDecoder('utf-8', {fatal: true}).decode(buffer);
  const out = Buffer.allocUnsafe(buffer.length);
  let n = 0;
  for (let i = 0; i < buffer.length; i++) {
    if (buffer[i] === 0x0d && buffer[i + 1] === 0x0a) continue;
    out[n++] = buffer[i];
  }
  return out.subarray(0, n);
}

const textSha256 = buffer => sha256(textLfBytes(buffer));

function contentHash(buffer, algorithm) {
  if (algorithm === BYTES_HASH) return sha256(buffer);
  if (algorithm === TEXT_HASH) return textSha256(buffer);
  throw new Error('unknown hash algorithm ' + algorithm);
}

module.exports = {BYTES_HASH, TEXT_HASH, sha256, textLfBytes, textSha256, contentHash};
