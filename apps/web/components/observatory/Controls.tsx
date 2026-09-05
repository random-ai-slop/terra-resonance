'use client';
import { useId, useState } from 'react';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
export function Choice({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
}) {
  const id = useId();
  return (
    <div className="control">
      <label id={id}>{label}</label>
      <Select
        value={value}
        onValueChange={(v) => v !== null && onChange(v)}
        items={options}
      >
        <SelectTrigger aria-labelledby={id}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
export function Range({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (v: number) => void;
}) {
  const id = useId();
  return (
    <div className="range-control">
      <div>
        <label id={id}>{label}</label>
        <output>
          {value.toLocaleString('en', { maximumFractionDigits: 3 })}
          {unit}
        </output>
      </div>
      <Slider
        aria-labelledby={id}
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={(v) => onChange(Array.isArray(v) ? v[0] : v)}
      />
    </div>
  );
}
export function Toggle({
  label,
  checked,
  onChange,
  disabled = false,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  const id = useId();
  return (
    <div className="toggle-control">
      <label htmlFor={id}>{label}</label>
      <Switch
        id={id}
        checked={checked}
        onCheckedChange={onChange}
        disabled={disabled}
      />
    </div>
  );
}
export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
}) {
  const id = useId();
  // Keep incomplete keyboard input (a minus sign, exponent or empty field)
  // local until blur/Enter. Only committed finite values enter scientific state.
  const [draft, setDraft] = useState<{ base: number; text: string } | null>(
    null,
  );
  const valid = (v: number) =>
    Number.isFinite(v) &&
    (min === undefined || v >= min) &&
    (max === undefined || v <= max);
  return (
    <label className="number-field" htmlFor={id}>
      <span>{label}</span>
      <Input
        id={id}
        type="number"
        value={draft?.base === value ? draft.text : String(value)}
        min={min}
        max={max}
        step={step}
        onChange={(e) => setDraft({ base: value, text: e.target.value })}
        onBlur={(e) => {
          const v = e.currentTarget.valueAsNumber;
          if (e.currentTarget.value.trim() && valid(v)) onChange(v);
          setDraft(null);
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter') e.currentTarget.blur();
          if (e.key === 'Escape') {
            setDraft(null);
            e.currentTarget.value = String(value);
            e.currentTarget.blur();
          }
        }}
      />
    </label>
  );
}
