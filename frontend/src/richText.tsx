import { Fragment } from "react";

/** Minimal inline markdown: **bold** + line breaks → React nodes. */
export function renderRich(text: string) {
  const lines = text.split("\n");
  return lines.map((line, li) => (
    <Fragment key={li}>
      {line.split(/(\*\*[^*]+\*\*)/g).map((seg, si) =>
        seg.startsWith("**") && seg.endsWith("**") ? (
          <strong key={si}>{seg.slice(2, -2)}</strong>
        ) : (
          <Fragment key={si}>{seg}</Fragment>
        )
      )}
      {li < lines.length - 1 && <br />}
    </Fragment>
  ));
}
