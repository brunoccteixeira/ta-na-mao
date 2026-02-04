import { loadBenefitsCatalogServer, getAllBenefitsServer, getStatesWithBenefitsServer } from '../../src/engine/catalog.server';
import HomeClient from './HomeClient';

export default function HomePage() {
  const catalog = loadBenefitsCatalogServer();

  const totalBenefits = getAllBenefitsServer(catalog).length;
  const federalCount = catalog.federal.length;
  const statesCovered = getStatesWithBenefitsServer(catalog).length;
  const sectoralCount = catalog.sectoral.length;

  return (
    <HomeClient
      totalBenefits={totalBenefits}
      federalCount={federalCount}
      statesCovered={statesCovered}
      sectoralCount={sectoralCount}
    />
  );
}
