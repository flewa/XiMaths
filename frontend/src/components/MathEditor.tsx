"use client";

import { closeBrackets, closeBracketsKeymap } from "@codemirror/autocomplete";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { markdown } from "@codemirror/lang-markdown";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { EditorState, Transaction } from "@codemirror/state";
import { EditorView, drawSelection, keymap, placeholder as placeholderText } from "@codemirror/view";
import { tags } from "@lezer/highlight";
import { useEffect, useEffectEvent, useRef } from "react";

import { SNIPPETS, type Snippet, applySnippet } from "@/lib/latex";

const LINE_HEIGHT = 1.5;

// Couleurs reprises des jetons du thème : l'éditeur suit le mode sombre sans rien recharger.
const theme = EditorView.theme({
  "&": { backgroundColor: "transparent", color: "var(--ink)" },
  "&.cm-focused": { outline: "none" },
  ".cm-scroller": { fontFamily: "inherit", lineHeight: String(LINE_HEIGHT) },
  ".cm-content": { padding: "8px 12px", caretColor: "var(--ink)" },
  ".cm-line": { padding: "0" },
  ".cm-cursor": { borderLeftColor: "var(--ink)" },
  ".cm-placeholder": { color: "var(--ash)" },
  "&.cm-focused .cm-selectionBackground, .cm-selectionBackground": {
    backgroundColor: "color-mix(in srgb, var(--ink) 16%, transparent)",
  },
});

const highlight = HighlightStyle.define([
  { tag: tags.heading, fontWeight: "bold" },
  { tag: tags.strong, fontWeight: "bold" },
  { tag: tags.emphasis, fontStyle: "italic" },
  { tag: tags.link, textDecoration: "underline" },
  { tag: [tags.processingInstruction, tags.monospace, tags.meta], color: "var(--mute)" },
]);

/** Éditeur Markdown + LaTeX, avec une barre de symboles. Remplace un textarea : même
 * valeur contrôlée, même `onChange`. */
export function MathEditor({
  id,
  label,
  value,
  onChange,
  rows = 8,
  placeholder = "",
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  rows?: number;
  placeholder?: string;
}) {
  const parent = useRef<HTMLDivElement>(null);
  const view = useRef<EditorView | null>(null);
  const emit = useEffectEvent((text: string) => onChange(text));
  const currentValue = useEffectEvent(() => value);

  useEffect(() => {
    const editor = new EditorView({
      parent: parent.current!,
      state: EditorState.create({
        doc: currentValue(),
        extensions: [
          history(),
          drawSelection(),
          closeBrackets(),
          // Pas de Tab qui indente : Tab sort de l'éditeur, comme d'un champ de formulaire.
          keymap.of([...closeBracketsKeymap, ...defaultKeymap, ...historyKeymap]),
          markdown(),
          syntaxHighlighting(highlight),
          EditorView.lineWrapping,
          placeholderText(placeholder),
          theme,
          EditorView.theme({ ".cm-content": { minHeight: `${rows * LINE_HEIGHT}em` } }),
          EditorView.contentAttributes.of({ id, "aria-label": label }),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) emit(update.state.doc.toString());
          }),
        ],
      }),
    });
    view.current = editor;
    return () => {
      editor.destroy();
      view.current = null;
    };
  }, [id, label, rows, placeholder]);

  // Valeur changée hors de l'éditeur (envoi, brouillon restauré) : on la reprend, sans
  // l'ajouter à l'historique d'annulation.
  useEffect(() => {
    const editor = view.current;
    if (editor && editor.state.doc.toString() !== value) {
      editor.dispatch({
        changes: { from: 0, to: editor.state.doc.length, insert: value },
        annotations: Transaction.addToHistory.of(false),
      });
    }
  }, [value]);

  function insert(snippet: Snippet) {
    const editor = view.current;
    if (!editor) return;
    const { from, to } = editor.state.selection.main;
    const edit = applySnippet(editor.state.doc.toString(), from, to, snippet);
    editor.dispatch({
      changes: { from: edit.from, to: edit.to, insert: edit.insert },
      selection: { anchor: edit.anchor, head: edit.head },
      scrollIntoView: true,
      userEvent: "input",
    });
    editor.focus();
  }

  return (
    <div className="rounded-sm border border-hairline bg-surface-soft transition-colors focus-within:border-ink focus-within:bg-canvas">
      <div role="group" aria-label="Symboles LaTeX" className="flex flex-wrap gap-0.5 border-b border-hairline p-1">
        {SNIPPETS.map((snippet) => (
          <button
            key={snippet.title}
            type="button"
            title={snippet.title}
            aria-label={snippet.title}
            // Garde la sélection de l'éditeur pendant le clic.
            onMouseDown={(event) => event.preventDefault()}
            onClick={() => insert(snippet)}
            className="min-w-8 rounded-sm px-1.5 py-0.5 text-sm text-body hover:bg-surface-card hover:text-ink"
          >
            {snippet.label}
          </button>
        ))}
      </div>
      <div ref={parent} style={{ minHeight: `calc(${rows * LINE_HEIGHT}em + 16px)` }} />
    </div>
  );
}
