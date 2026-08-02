---
title: Markdown Renderer Test
author: Codex Skills
---

# Rich document

This document contains **formatted text**, a [link](https://pandoc.org/), and
the inline equation \(E=mc^2\) followed by the display equation

$$
\int_0^\infty e^{-x^2}\,dx = \frac{\sqrt{\pi}}{2}.
$$

~~~python
def square(value: int) -> int:
    return value * value
~~~

~~~mermaid
graph TD
    accTitle: Rendering flow
    accDescr: Markdown becomes a document
    A[Markdown] --> B[Document]
~~~

~~~dot
digraph {
    Markdown -> Document;
}
~~~
