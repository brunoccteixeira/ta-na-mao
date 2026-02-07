'use client';

/**
 * DateSelect - Three selects for day/month/year
 *
 * Calculates age automatically
 */

import { useMemo, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

interface Props {
  day: number | undefined;
  month: number | undefined;
  year: number | undefined;
  onChangeDay: (day: number) => void;
  onChangeMonth: (month: number) => void;
  onChangeYear: (year: number) => void;
  className?: string;
}

export default function DateSelect({
  day,
  month,
  year,
  onChangeDay,
  onChangeMonth,
  onChangeYear,
  className = '',
}: Props) {
  const currentYear = new Date().getFullYear();

  // Generate days based on selected month/year
  const maxDay = useMemo(() => {
    if (month && year) return new Date(year, month, 0).getDate();
    if (month) return new Date(2024, month, 0).getDate(); // leap year as safe default
    return 31;
  }, [month, year]);

  const days = Array.from({ length: maxDay }, (_, i) => i + 1);

  // Reset day if it exceeds the max for the selected month
  useEffect(() => {
    if (day && day > maxDay) {
      onChangeDay(maxDay);
    }
  }, [maxDay, day, onChangeDay]);

  const months = [
    { value: 1, label: 'Janeiro' },
    { value: 2, label: 'Fevereiro' },
    { value: 3, label: 'Março' },
    { value: 4, label: 'Abril' },
    { value: 5, label: 'Maio' },
    { value: 6, label: 'Junho' },
    { value: 7, label: 'Julho' },
    { value: 8, label: 'Agosto' },
    { value: 9, label: 'Setembro' },
    { value: 10, label: 'Outubro' },
    { value: 11, label: 'Novembro' },
    { value: 12, label: 'Dezembro' },
  ];
  const years = Array.from({ length: 100 }, (_, i) => currentYear - i);

  // Calculate age
  const age = useMemo(() => {
    if (!day || !month || !year) return null;

    const birthDate = new Date(year, month - 1, day);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    return age;
  }, [day, month, year]);

  const selectClass = `
    appearance-none w-full py-3 px-4 pr-10 text-[var(--text-primary)] font-medium
    bg-[var(--input-bg)] border-2 border-[var(--input-border)] rounded-xl
    focus:border-emerald-500 focus:outline-none transition-colors cursor-pointer
  `;

  return (
    <div className={className}>
      <div className="grid grid-cols-3 gap-3">
        {/* Day */}
        <div className="relative">
          <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">Dia</label>
          <select
            value={day ?? ''}
            onChange={(e) => onChangeDay(parseInt(e.target.value, 10))}
            className={selectClass}
          >
            <option value="">Dia</option>
            {days.map((d) => (
              <option key={d} value={d}>
                {d.toString().padStart(2, '0')}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 bottom-3.5 w-4 h-4 text-[var(--text-tertiary)] pointer-events-none" />
        </div>

        {/* Month */}
        <div className="relative">
          <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">Mês</label>
          <select
            value={month ?? ''}
            onChange={(e) => onChangeMonth(parseInt(e.target.value, 10))}
            className={selectClass}
          >
            <option value="">Mês</option>
            {months.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label.substring(0, 3)}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 bottom-3.5 w-4 h-4 text-[var(--text-tertiary)] pointer-events-none" />
        </div>

        {/* Year */}
        <div className="relative">
          <label className="block text-xs text-[var(--text-tertiary)] mb-1.5">Ano</label>
          <select
            value={year ?? ''}
            onChange={(e) => onChangeYear(parseInt(e.target.value, 10))}
            className={selectClass}
          >
            <option value="">Ano</option>
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 bottom-3.5 w-4 h-4 text-[var(--text-tertiary)] pointer-events-none" />
        </div>
      </div>

      {/* Age display */}
      {age !== null && (
        <div className="mt-3 p-3 bg-emerald-50 dark:bg-emerald-500/10 rounded-xl">
          <p className="text-sm text-emerald-700 dark:text-emerald-400">
            <span className="font-semibold">{age} anos</span>
            {age >= 60 && ' - Você pode ter direito a benefícios para idosos'}
            {age < 18 && ' - Menor de idade'}
            {age >= 18 && age < 60 && ''}
          </p>
        </div>
      )}
    </div>
  );
}
