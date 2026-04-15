export function TypingIndicator() {
  return (
    <div className="flex items-end gap-2 animate-fade-in">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground text-xs font-medium">
        AI
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-white border border-border px-4 py-3 shadow-sm">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-muted-foreground animate-blink"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
    </div>
  )
}
