/**
 * Cards - A2UI Component Cards
 *
 * Re-exports all card components and provides a dynamic renderer
 */

import { UIComponent, UIComponentType } from '../../api/chatClient';
import ChecklistCard from './ChecklistCard';
import MedicationListCard from './MedicationListCard';
import PharmacyCard from './PharmacyCard';
import BenefitCard from './BenefitCard';
import CrasCard from './CrasCard';
import OrderStatusCard from './OrderStatusCard';
import AlertCard from './AlertCard';

export {
  ChecklistCard,
  MedicationListCard,
  PharmacyCard,
  BenefitCard,
  CrasCard,
  OrderStatusCard,
  AlertCard,
};

// Component mapping
const COMPONENT_MAP: Record<UIComponentType, React.ComponentType<{ data: any }>> = {
  checklist: ChecklistCard,
  medication_list: MedicationListCard,
  pharmacy_card: PharmacyCard,
  benefit_card: BenefitCard,
  cras_card: CrasCard,
  order_status: OrderStatusCard,
  alert: AlertCard,
  status_badge: AlertCard, // Use alert for status badges
  map_location: CrasCard, // Use CRAS card for map locations
};

interface DynamicCardProps {
  component: UIComponent;
}

/**
 * DynamicCard - Renders any A2UI component dynamically
 */
export function DynamicCard({ component }: DynamicCardProps) {
  const CardComponent = COMPONENT_MAP[component.type];

  if (!CardComponent) {
    console.warn(`Unknown component type: ${component.type}`);
    return (
      <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
        <p className="text-sm text-slate-400">
          Componente não suportado: {component.type}
        </p>
        <pre className="mt-2 text-xs text-slate-500 overflow-auto">
          {JSON.stringify(component.data, null, 2)}
        </pre>
      </div>
    );
  }

  return <CardComponent data={component.data} />;
}

/**
 * CardList - Renders a list of A2UI components
 */
interface CardListProps {
  components: UIComponent[];
  className?: string;
}

export function CardList({ components, className = '' }: CardListProps) {
  if (!components || components.length === 0) return null;

  return (
    <div className={`space-y-3 ${className}`}>
      {components.map((component, index) => (
        <DynamicCard key={`${component.type}-${index}`} component={component} />
      ))}
    </div>
  );
}
