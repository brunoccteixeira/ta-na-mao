/**
 * CriteriaSection — groups CriterionCards under a category header.
 */

import {
  FileText,
  DollarSign,
  Users,
  Briefcase,
  Home,
  ClipboardList,
} from 'lucide-react';
import type { GroupedCriteria } from '../../utils/criteriaGrouping';
import CriterionCard from './CriterionCard';

interface CriteriaSectionProps {
  group: GroupedCriteria;
}

const ICON_MAP: Record<string, React.ReactNode> = {
  FileText: <FileText className="w-5 h-5" />,
  DollarSign: <DollarSign className="w-5 h-5" />,
  Users: <Users className="w-5 h-5" />,
  Briefcase: <Briefcase className="w-5 h-5" />,
  Home: <Home className="w-5 h-5" />,
  ClipboardList: <ClipboardList className="w-5 h-5" />,
};

export default function CriteriaSection({ group }: CriteriaSectionProps) {
  return (
    <section className="mb-6">
      {/* Group header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-[var(--text-secondary)]">
          {ICON_MAP[group.lucideIcon] || ICON_MAP.ClipboardList}
        </span>
        <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wide">
          {group.label}
        </h3>
      </div>

      {/* Criterion cards */}
      <div className="space-y-2" role="list" aria-label={group.label}>
        {group.rules.map((evaluatedRule, idx) => (
          <CriterionCard key={idx} evaluatedRule={evaluatedRule} />
        ))}
      </div>
    </section>
  );
}
