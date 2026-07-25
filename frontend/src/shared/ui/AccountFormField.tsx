import type { ChangeEventHandler, HTMLInputAutoCompleteAttribute, HTMLInputTypeAttribute } from "react";

interface AccountFormFieldProps {
  autoComplete: HTMLInputAutoCompleteAttribute;
  label: string;
  name: string;
  onChange: ChangeEventHandler<HTMLInputElement>;
  value: string;
  minLength?: number;
  required?: boolean;
  type?: HTMLInputTypeAttribute;
}

export const AccountFormField = ({ label, ...inputProps }: AccountFormFieldProps) => (
  <label className="block">
    <span className="mb-2 block text-sm font-medium text-(--app-ink)">{label}</span>
    <input
      {...inputProps}
      className="w-full rounded-2xl border border-(--app-border) bg-white px-4 py-3 text-base outline-none transition focus:border-(--app-accent)"
    />
  </label>
);
