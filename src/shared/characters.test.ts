import { describe, expect, it } from "vitest";
import { countCharacters, isValidDraftLength, normalizeLineEndings } from "./characters";

describe("shared Unicode count", () => {
  it.each([
    [800, false],
    [801, true],
    [1000, true],
    [1001, false],
  ] as const)("boundary %i", (size, valid) => {
    const draft = "😀".repeat(size);
    expect(countCharacters(draft)).toBe(size);
    expect(isValidDraftLength(countCharacters(draft))).toBe(valid);
  });
  it("counts whitespace, Korean, CRLF, CR, combining marks and emoji code points", () => {
    expect(normalizeLineEndings("가\r\n \r😀\n")).toBe("가\n \n😀\n");
    expect(countCharacters("가\r\n \r😀\n")).toBe(6);
    expect(countCharacters("👨‍👩‍👧‍👦")).toBe(7);
    expect(countCharacters("e\u0301")).toBe(2);
    expect(countCharacters(" ")).toBe(1);
  });
});
