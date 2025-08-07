
// Utility to load items from the final_assets directory structure

export interface FinalAssetItem {
  name: string;
  item_type: string;
  variants: Record<string, string>;
  default_inputs?: any[];
  path: string; // Path from the consolidate script
}

export interface ProcessedItem {
  id: string;
  name: string;
  type: string;
  category: string;
  image: string;
  keywords: string[];
  description?: string;
  variants?: Record<string, string>;
  path: string; // Directory path for context
  default_inputs?: any[];
}

// Map directory paths to human-readable categories
const CATEGORY_MAP: Record<string, string> = {
  'mics': 'Microphones',
  'mics/boom': 'Microphones - Boom',
  'mics/hand_held': 'Microphones - Hand Held',
  'mics/headset': 'Microphones - Headset', 
  'mics/straight': 'Microphones - Straight',
  'more': 'Equipment & Accessories',
  'more/laptop': 'Computers & Tech',
  'more/mixer': 'Audio Equipment',
  'more/dj_gear': 'DJ Equipment',
  'more/video': 'Video Equipment',
  'more/furniture': 'Furniture',
  'more/rack': 'Racks & Cases',
  'drums': 'Drums',
  'drums/hardware': 'Drums - Hardware', 
  'drums/individual_drums': 'Drums - Individual',
  'drums/drum_kits': 'Drum Kits',
  'guitars': 'Guitars',
  'keys': 'Keyboards & Piano',
  'amps': 'Amplifiers',
  'amps/bass': 'Bass Amplifiers',
  'strings': 'String Instruments',
  'winds': 'Wind Instruments', 
  'percussion': 'Percussion',
  'people': 'People',
  'stagecraft': 'Stage & Production',
  'outputs': 'Outputs',
  'symbols': 'Symbols',
  'numerals': 'Numbers',
  'alphabet': 'Letters'
};

/**
 * Load all items from the consolidated items.json file.
 */
export async function loadFinalAssets(): Promise<ProcessedItem[]> {
  try {
    const response = await fetch(`/final_assets/items.json`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const itemsData: FinalAssetItem[] = await response.json();
    return itemsData.map(item => processItem(item, item.path, getCategoryPath(item.path))).filter(Boolean) as ProcessedItem[];
  } catch (error) {
    console.error('Error loading final assets:', error);
    return [];
  }
}

function getCategoryPath(path: string): string {
    const parts = path.split('/');
    if (parts.length > 1) {
        return parts.slice(0, -1).join('/');
    }
    return parts[0];
}

function processItem(itemData: FinalAssetItem, path: string, categoryPath: string): ProcessedItem | null {
  if (!itemData.name || !itemData.variants) {
    return null;
  }
  
  const defaultImage = itemData.variants.default || Object.values(itemData.variants)[0];
  if (!defaultImage) {
    return null;
  }
  
  const imagePath = `/final_assets/${path}/${defaultImage}`;
  const category = CATEGORY_MAP[categoryPath] || categoryPath;
  
  const keywords = [
    itemData.name.toLowerCase(),
    itemData.item_type.toLowerCase(),
    ...itemData.name.toLowerCase().split(/\s+/),
    ...category.toLowerCase().split(/\s+/),
    categoryPath.split('/').join(' ').toLowerCase()
  ].filter(Boolean);
  
  return {
    id: `final-asset-${path.replace(/[^a-zA-Z0-9]/g, '-')}`,
    name: itemData.name,
    type: itemData.item_type,
    category,
    image: imagePath,
    keywords,
    description: `${itemData.name} - ${category}`,
    variants: itemData.variants,
    path,
    default_inputs: itemData.default_inputs
  };
}

/**
 * Filter items based on criteria
 */
export function filterItems(items: ProcessedItem[], criteria: {
  includeInputs?: boolean;
  includeAccessories?: boolean;
  includeSymbols?: boolean;
  categories?: string[];
}): ProcessedItem[] {
  return items.filter(item => {
    if (criteria.includeInputs === false && item.type === 'input') return false;
    if (criteria.includeAccessories === false && item.type === 'accessory') return false;
    if (criteria.includeSymbols === false && item.type === 'symbol') return false;
    if (criteria.categories && !criteria.categories.includes(item.category)) return false;
    return true;
  });
}
