export function confirmDestructiveDemoReset(): boolean {
  return window.confirm(
    "Demo seed/reset replaces all local prototype data, including uploaded documents. Continue only if the data is disposable.",
  );
}
