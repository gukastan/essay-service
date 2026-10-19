export const MIN_CHARACTERS = 801;
export const MAX_CHARACTERS = 1000;

export function normalizeLineEndings(text: string): string {
  return text.replace(/\r\n?/g, "\n");
}

export function countCharacters(text: string): number {
  return Array.from(normalizeLineEndings(text)).length;
}

export function isValidDraftLength(count: number): boolean {
  return count >= MIN_CHARACTERS && count <= MAX_CHARACTERS;
}
